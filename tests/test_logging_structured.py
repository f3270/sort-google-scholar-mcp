import asyncio
import logging
from datetime import datetime
from pathlib import Path

import pytest

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import (
    DownloadMetadata,
    Paper,
    PDFDownloadResult,
    QueryResult,
    QuerySource,
    SearchParams,
    SearchSession,
)
from sortgs_mcp.tools import download as download_tool
from sortgs_mcp.tools import index as index_tool
from sortgs_mcp.tools import query as query_tool
from sortgs_mcp.tools import search as search_tool


class FakeScholarSearcher:
    def __init__(self, papers):
        self._papers = papers

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    async def search(self, params):
        return self._papers


class FakeDownloader:
    def __init__(self, result: PDFDownloadResult) -> None:
        self.result = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    async def download_batch(
        self, papers, pdf_dir, session_id, project_root=None, force_redownload=False
    ):
        return self.result


class FakeEmbedder:
    def __init__(self, dimension: int = 3) -> None:
        self.dimension = dimension

    @property
    def embedding_dim(self) -> int:
        return self.dimension

    @property
    def model_name(self) -> str:
        return "fake-model"

    def embed_texts(
        self, texts: list[str], batch_size: int = 1000
    ) -> list[list[float]]:
        return [[0.1] * self.dimension for _ in texts]


class FakeVectorStore:
    def __init__(self) -> None:
        self.added = []

    def add_documents(
        self, session_id: str, chunks: list[dict], embeddings: list[list[float]]
    ) -> int:
        self.added.append((session_id, len(chunks)))
        return len(chunks)


class FakeRetriever:
    async def answer_question(self, question, session_id, top_k=5):
        source = QuerySource(
            paper_title="Paper 1",
            chunk_text="Chunk",
            relevance_score=0.9,
            metadata={"paper_rank": 1},
        )
        return QueryResult(
            question=question,
            answer="Answer",
            sources=[source],
            session_id=session_id,
        )


def _make_paper(rank: int, title: str, pdf_url: str | None = None) -> Paper:
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
        pdf_url=pdf_url,
        cit_per_year=1,
    )


def _create_session(
    tmp_path: Path, papers: list[Paper], indexed: bool = False
) -> tuple[str, SessionManager]:
    params = SearchParams(
        keywords="test",
        num_results=10,
        sort_by="Citations",
    )
    session_id = "session-id"
    session = SearchSession(
        session_id=session_id,
        params=params,
        papers=papers,
        indexed=indexed,
    )
    manager = SessionManager(tmp_path)
    manager.save_session(session)
    return session_id, manager


def _find_record(caplog, message: str):
    for record in caplog.records:
        if record.getMessage() == message:
            return record
    raise AssertionError(f"Log message not found: {message}")


def test_search_papers_structured_logging(tmp_path, sample_papers, monkeypatch, caplog):
    manager = SessionManager(tmp_path)
    monkeypatch.setattr(search_tool, "session_manager", manager)
    monkeypatch.setattr(search_tool.settings, "data_dir", tmp_path)
    monkeypatch.setattr(
        "sortgs_mcp.core.scholar.ScholarSearcher",
        lambda debug=False: FakeScholarSearcher(sample_papers),
    )

    caplog.set_level(logging.INFO)
    asyncio.run(
        search_tool.search_papers(
            keywords="transformers",
            num_results=10,
            sort_by="Citations",
            debug=True,
        )
    )

    record = _find_record(caplog, "search_papers called")
    assert record.keywords == "transformers"
    assert record.num_results == 10


def test_download_papers_structured_logging(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = _create_session(
        tmp_path,
        [_make_paper(1, "Paper One", pdf_url="https://example.com/paper.pdf")],
    )
    monkeypatch.setattr(download_tool, "session_manager", manager)

    metadata = DownloadMetadata(
        rank=1,
        title="Paper One",
        pdf_path="data/sessions/session-id/pdfs/paper_001_paper_one.pdf",
        file_size_bytes=100,
        download_timestamp=datetime.now(),
        status="downloaded",
    )
    result = PDFDownloadResult(
        session_id=session_id,
        downloaded=1,
        skipped=0,
        failed=0,
        pdf_paths=[metadata.pdf_path],
        failed_papers=[],
        download_metadata=[metadata],
        error=None,
    )

    fake_downloader = FakeDownloader(result)
    monkeypatch.setattr(
        download_tool, "PDFDownloader", lambda **kwargs: fake_downloader
    )

    caplog.set_level(logging.INFO)
    asyncio.run(download_tool.download_papers(session_id, max_papers=2))

    record = _find_record(caplog, "download_papers called")
    assert record.session_id == session_id
    assert record.max_papers == 2

    record = _find_record(caplog, "Downloaded PDFs for session")
    assert record.downloaded == 1
    assert record.failed == 0


def test_index_papers_structured_logging(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = _create_session(
        tmp_path,
        [_make_paper(1, "Paper One", pdf_url="https://example.com/paper.pdf")],
    )
    monkeypatch.setattr(index_tool, "session_manager", manager)

    pdf_dir = settings.pdf_download_dir(session_id)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    (pdf_dir / "paper_001_paper.pdf").write_text("pdf", encoding="utf-8")

    def fake_chunker(pdf_path, paper, session_id, chunk_size, chunk_overlap):
        return [
            {
                "text": "text",
                "metadata": {
                    "session_id": session_id,
                    "paper_title": paper.title,
                    "paper_authors": paper.authors,
                    "paper_year": paper.year,
                    "paper_citations": paper.citations,
                    "paper_rank": paper.rank,
                    "source_url": paper.source_url,
                    "chunk_index": 0,
                    "total_chunks": 1,
                },
            }
        ]

    monkeypatch.setattr(
        index_tool, "get_embedding_service", lambda model: FakeEmbedder()
    )
    monkeypatch.setattr(
        index_tool, "VectorStore", lambda *args, **kwargs: FakeVectorStore()
    )
    monkeypatch.setattr(index_tool, "parse_and_chunk_pdf", fake_chunker)

    caplog.set_level(logging.INFO)
    asyncio.run(index_tool.index_papers(session_id, max_chunks=100))

    record = _find_record(caplog, "index_papers completed")
    assert record.session_id == session_id
    assert record.chunks_created == 1


def test_query_and_list_sessions_logging(tmp_path, monkeypatch, caplog):
    manager = SessionManager(tmp_path)
    session = SearchSession(
        session_id="session-2",
        params=SearchParams(keywords="test", num_results=10, sort_by="Citations"),
        papers=[],
        indexed=True,
    )
    manager.save_session(session)
    monkeypatch.setattr(query_tool, "session_manager", manager)
    monkeypatch.setattr(query_tool, "RAGRetriever", lambda **kwargs: FakeRetriever())
    monkeypatch.setattr(query_tool, "_get_openai_client", lambda: object())
    monkeypatch.setattr(query_tool, "_get_embedder", lambda: object())
    monkeypatch.setattr(query_tool, "_get_vectorstore", lambda: object())

    caplog.set_level(logging.INFO)
    asyncio.run(
        query_tool.query_papers("What is RAG?", session_id="session-2", top_k=2)
    )
    asyncio.run(query_tool.list_sessions())

    record = _find_record(caplog, "query_papers answered")
    assert record.session_id == "session-2"
    assert record.top_k == 2

    record = _find_record(caplog, "list_sessions called")
    assert record.session_count == 1
