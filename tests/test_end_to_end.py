from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import DownloadMetadata, PDFDownloadResult
from sortgs_mcp.tools import download as download_tool
from sortgs_mcp.tools import index as index_tool
from sortgs_mcp.tools import query as query_tool
from sortgs_mcp.tools import search as search_tool


@dataclass
class FakeEmbedder:
    embedding_dim: int = 3
    model_name: str = "fake-model"

    def embed_texts(self, texts, batch_size=1000):
        return [[float(len(text))] * self.embedding_dim for text in texts]

    def embed_single(self, text):
        return [float(len(text))] * self.embedding_dim


class FakeOpenAI:
    async def generate_answer(self, question: str, context: str) -> str:
        return "Synthesized answer"


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
    def __init__(self, pdf_dir: Path, result: PDFDownloadResult):
        self.pdf_dir = pdf_dir
        self.result = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    async def download_batch(
        self, papers, pdf_dir, session_id, project_root=None, force_redownload=False
    ):
        pdf_dir.mkdir(parents=True, exist_ok=True)
        for paper in papers:
            pdf_path = pdf_dir / f"paper_{paper.rank:03d}_test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 test")
        return self.result


class FakeVectorStore:
    def __init__(self, *args, **kwargs):
        self._documents = []

    def add_documents(self, session_id, chunks, embeddings):
        self._documents.extend(chunks)
        return len(chunks)

    def query(self, query_embedding, session_id, k=5):
        hits = []
        for chunk in self._documents[:k]:
            hits.append(
                {
                    "id": "fake",
                    "text": chunk.get("text", ""),
                    "metadata": chunk.get("metadata", {}),
                    "distance": 0.1,
                }
            )
        return hits


@pytest.mark.asyncio
async def test_full_workflow_with_isolation(
    isolated_environment, sample_papers, monkeypatch
):
    data_dir = isolated_environment["data_dir"]
    settings.data_dir = data_dir
    settings.sessions_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)

    manager = SessionManager(data_dir)
    monkeypatch.setattr(search_tool, "session_manager", manager)
    monkeypatch.setattr(download_tool, "session_manager", manager)
    monkeypatch.setattr(index_tool, "session_manager", manager)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    monkeypatch.setattr(
        "sortgs_mcp.core.scholar.ScholarSearcher",
        lambda debug=False: FakeScholarSearcher(sample_papers),
    )

    search_result = await search_tool.search_papers(
        keywords="transformers",
        num_results=10,
        sort_by="Citations",
        debug=True,
    )
    session_id = search_result["session_id"]

    pdf_dir = settings.pdf_download_dir(session_id)
    metadata = [
        DownloadMetadata(
            rank=paper.rank,
            title=paper.title,
            pdf_path=str(pdf_dir / f"paper_{paper.rank:03d}_test.pdf"),
            file_size_bytes=100,
        )
        for paper in sample_papers
    ]
    download_result = PDFDownloadResult(
        session_id=session_id,
        downloaded=len(sample_papers),
        skipped=0,
        failed=0,
        pdf_paths=[meta.pdf_path for meta in metadata],
        download_metadata=metadata,
    )

    monkeypatch.setattr(
        download_tool,
        "PDFDownloader",
        lambda **kwargs: FakeDownloader(pdf_dir, download_result),
    )

    download_response = await download_tool.download_papers(
        session_id=session_id, max_papers=2
    )
    assert download_response["downloaded"] == 2

    fake_embedder = FakeEmbedder()
    shared_store = FakeVectorStore()
    monkeypatch.setattr(index_tool, "get_embedding_service", lambda name: fake_embedder)
    monkeypatch.setattr(index_tool, "VectorStore", lambda *args, **kwargs: shared_store)

    def fake_parse_and_chunk_pdf(
        pdf_path, paper, session_id, chunk_size=1000, chunk_overlap=200
    ):
        return [
            {
                "text": "Chunk text",
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
        index_tool, "parse_and_chunk_pdf", fake_parse_and_chunk_pdf
    )

    index_response = await index_tool.index_papers(session_id=session_id)
    assert index_response["papers_indexed"] == 2
    assert index_response["chunks_created"] == 2

    query_tool._openai_client = None
    query_tool._vectorstore = None
    query_tool._embedder = None
    monkeypatch.setattr(query_tool, "_get_openai_client", lambda: FakeOpenAI())
    monkeypatch.setattr(query_tool, "_get_embedder", lambda: fake_embedder)
    monkeypatch.setattr(query_tool, "_get_vectorstore", lambda: shared_store)

    query_response = await query_tool.query_papers(
        question="What is a transformer?",
        session_id=session_id,
        top_k=2,
    )
    assert query_response["answer"] == "Synthesized answer"
    assert len(query_response["sources"]) == 2
