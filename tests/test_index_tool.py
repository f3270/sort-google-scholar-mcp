import asyncio
from pathlib import Path

import pytest

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import Paper, SearchParams, SearchSession
from sortgs_mcp.tools import index as index_tool


def make_paper(rank: int, title: str) -> Paper:
    return Paper(
        rank=rank,
        title=title,
        authors="A Author",
        citations=1,
        year=2020,
        publisher="Test Publisher",
        venue="Test Venue",
        content_snippet="Snippet",
        source_url="https://example.com",
        pdf_url="https://example.com/paper.pdf",
        cit_per_year=1,
    )


def create_session(tmp_path: Path, papers: list[Paper]) -> tuple[str, SessionManager]:
    params = SearchParams(
        keywords="test",
        num_results=10,
        sort_by="Citations",
    )
    session_id = "session-id"
    session = SearchSession(session_id=session_id, params=params, papers=papers)
    manager = SessionManager(tmp_path)
    manager.save_session(session)
    return session_id, manager


def write_pdf_files(pdf_dir: Path, ranks: list[int]) -> None:
    pdf_dir.mkdir(parents=True, exist_ok=True)
    for rank in ranks:
        (pdf_dir / f"paper_{rank:03d}_paper.pdf").write_text("pdf", encoding="utf-8")


def make_chunks(session_id: str, paper: Paper, total: int) -> list[dict]:
    return [
        {
            "text": f"text {idx}",
            "metadata": {
                "session_id": session_id,
                "paper_title": paper.title,
                "paper_authors": paper.authors,
                "paper_year": paper.year,
                "paper_citations": paper.citations,
                "paper_rank": paper.rank,
                "source_url": paper.source_url,
                "chunk_index": idx,
                "total_chunks": total,
            },
        }
        for idx in range(total)
    ]


class FakeEmbedder:
    def __init__(self, dimension: int = 3, output_dim: int | None = None) -> None:
        self.dimension = dimension
        self.output_dim = output_dim if output_dim is not None else dimension
        self.embed_texts_calls: list[tuple[int, int]] = []
        self.batches_processed: list[int] = []

    @property
    def embedding_dim(self) -> int:
        return self.dimension

    @property
    def model_name(self) -> str:
        return "fake-model"

    def embed_texts(
        self, texts: list[str], batch_size: int = 1000
    ) -> list[list[float]]:
        self.embed_texts_calls.append((len(texts), batch_size))
        for i in range(0, len(texts), batch_size):
            self.batches_processed.append(len(texts[i : i + batch_size]))
        return [[0.1] * self.output_dim for _ in texts]


class FakeVectorStore:
    def __init__(
        self,
        persist_dir: Path,
        *,
        embedding_dim: int = 3,
        distance_metric: str = "cosine",
        model_name: str | None = None,
    ) -> None:
        self.embedding_dim = embedding_dim
        self.add_documents_calls: list[tuple[str, int]] = []

    def add_documents(
        self, session_id: str, chunks: list[dict], embeddings: list[list[float]]
    ) -> int:
        if embeddings and len(embeddings[0]) != self.embedding_dim:
            raise ValueError(
                f"Expected {self.embedding_dim} dims, got {len(embeddings[0])}"
            )
        self.add_documents_calls.append((session_id, len(chunks)))
        return len(chunks)


def setup_tool_env(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "embedding_batch_size", 1000)
    session_id, manager = create_session(
        tmp_path,
        [make_paper(1, "Paper One"), make_paper(2, "Paper Two")],
    )
    monkeypatch.setattr(index_tool, "session_manager", manager)
    return session_id


def test_index_papers_basic(tmp_path, monkeypatch):
    session_id = setup_tool_env(tmp_path, monkeypatch)
    pdf_dir = settings.pdf_download_dir(session_id)
    write_pdf_files(pdf_dir, [1, 2])

    fake_embedder = FakeEmbedder(dimension=3)
    fake_vectorstore = FakeVectorStore(tmp_path, embedding_dim=3)

    def fake_chunker(pdf_path, paper, session_id, chunk_size, chunk_overlap):
        return make_chunks(session_id, paper, 2)

    monkeypatch.setattr(
        index_tool, "get_embedding_service", lambda model: fake_embedder
    )
    monkeypatch.setattr(
        index_tool, "VectorStore", lambda *args, **kwargs: fake_vectorstore
    )
    monkeypatch.setattr(index_tool, "parse_and_chunk_pdf", fake_chunker)

    response = asyncio.run(index_tool.index_papers(session_id, max_chunks=1000))
    assert response["papers_indexed"] == 2
    assert response["chunks_created"] == 4
    assert not response["failed_papers"]

    saved = index_tool.session_manager.load_session(session_id)
    assert saved.indexed is True


def test_index_papers_no_pdfs(tmp_path, monkeypatch):
    session_id = setup_tool_env(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="No PDFs found"):
        asyncio.run(index_tool.index_papers(session_id))


def test_index_papers_partial_failure(tmp_path, monkeypatch):
    session_id = setup_tool_env(tmp_path, monkeypatch)
    pdf_dir = settings.pdf_download_dir(session_id)
    write_pdf_files(pdf_dir, [1, 2])

    fake_embedder = FakeEmbedder(dimension=3)
    fake_vectorstore = FakeVectorStore(tmp_path, embedding_dim=3)

    def fake_chunker(pdf_path, paper, session_id, chunk_size, chunk_overlap):
        if paper.rank == 2:
            return None
        return make_chunks(session_id, paper, 1)

    monkeypatch.setattr(
        index_tool, "get_embedding_service", lambda model: fake_embedder
    )
    monkeypatch.setattr(
        index_tool, "VectorStore", lambda *args, **kwargs: fake_vectorstore
    )
    monkeypatch.setattr(index_tool, "parse_and_chunk_pdf", fake_chunker)

    response = asyncio.run(index_tool.index_papers(session_id, max_chunks=1000))
    assert response["papers_indexed"] == 1
    assert "Paper Two" in response["failed_papers"]


def test_index_papers_max_chunks(tmp_path, monkeypatch):
    session_id = setup_tool_env(tmp_path, monkeypatch)
    pdf_dir = settings.pdf_download_dir(session_id)
    write_pdf_files(pdf_dir, [1, 2])

    fake_embedder = FakeEmbedder(dimension=3)
    fake_vectorstore = FakeVectorStore(tmp_path, embedding_dim=3)

    def fake_chunker(pdf_path, paper, session_id, chunk_size, chunk_overlap):
        return make_chunks(session_id, paper, 6000)

    monkeypatch.setattr(
        index_tool, "get_embedding_service", lambda model: fake_embedder
    )
    monkeypatch.setattr(
        index_tool, "VectorStore", lambda *args, **kwargs: fake_vectorstore
    )
    monkeypatch.setattr(index_tool, "parse_and_chunk_pdf", fake_chunker)

    response = asyncio.run(index_tool.index_papers(session_id, max_chunks=10000))
    assert response["chunks_created"] == 10000


def test_index_papers_validation(tmp_path, monkeypatch):
    session_id = setup_tool_env(tmp_path, monkeypatch)
    pdf_dir = settings.pdf_download_dir(session_id)
    write_pdf_files(pdf_dir, [1])

    with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
        asyncio.run(index_tool.index_papers(session_id, chunk_size=50))


def test_dimension_mismatch_error(tmp_path, monkeypatch):
    session_id = setup_tool_env(tmp_path, monkeypatch)
    pdf_dir = settings.pdf_download_dir(session_id)
    write_pdf_files(pdf_dir, [1])

    fake_embedder = FakeEmbedder(dimension=3, output_dim=2)
    fake_vectorstore = FakeVectorStore(tmp_path, embedding_dim=3)

    def fake_chunker(pdf_path, paper, session_id, chunk_size, chunk_overlap):
        return make_chunks(session_id, paper, 1)

    monkeypatch.setattr(
        index_tool, "get_embedding_service", lambda model: fake_embedder
    )
    monkeypatch.setattr(
        index_tool, "VectorStore", lambda *args, **kwargs: fake_vectorstore
    )
    monkeypatch.setattr(index_tool, "parse_and_chunk_pdf", fake_chunker)

    with pytest.raises(ValueError, match="Expected 3 dims, got 2"):
        asyncio.run(index_tool.index_papers(session_id, max_chunks=1000))
