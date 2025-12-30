"""Shared pytest fixtures for sortgs_mcp tests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import uuid

import pytest

from sortgs_mcp.models import Paper, SearchParams, SearchSession
from sortgs_mcp.rag.vectorstore import VectorStore


@pytest.fixture
def sample_paper() -> Paper:
    """Create a sample Paper instance for tests."""
    return Paper(
        rank=1,
        title="Attention Is All You Need",
        authors="Vaswani et al.",
        citations=50000,
        year=2017,
        publisher="NeurIPS",
        venue="Conference",
        content_snippet="We propose a new simple network architecture...",
        source_url="https://arxiv.org/abs/1706.03762",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        cit_per_year=6250,
    )


@pytest.fixture
def sample_papers() -> list[Paper]:
    """Create a list of sample Papers for tests."""
    return [
        Paper(
            rank=1,
            title="Attention Is All You Need",
            authors="Vaswani et al.",
            citations=50000,
            year=2017,
            publisher="NeurIPS",
            venue="Conference",
            content_snippet="Transformers architecture...",
            source_url="https://arxiv.org/abs/1706.03762",
            pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
            cit_per_year=6250,
        ),
        Paper(
            rank=2,
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors="Devlin et al.",
            citations=30000,
            year=2018,
            publisher="NAACL",
            venue="Conference",
            content_snippet="BERT architecture...",
            source_url="https://arxiv.org/abs/1810.04805",
            pdf_url="https://arxiv.org/pdf/1810.04805.pdf",
            cit_per_year=4285,
        ),
    ]


@pytest.fixture
def sample_search_params() -> SearchParams:
    """Create sample SearchParams for tests."""
    return SearchParams(
        keywords="transformers attention mechanism",
        num_results=10,
        sort_by="Citations",
        start_year=2017,
        end_year=2024,
        languages=["en"],
    )


@pytest.fixture
def sample_session(
    sample_search_params: SearchParams, sample_papers: list[Paper]
) -> SearchSession:
    """Create a sample SearchSession for tests."""
    return SearchSession(
        session_id=str(uuid.uuid4()),
        created_at=datetime.now(),
        params=sample_search_params,
        papers=sample_papers,
        papers_count=len(sample_papers),
        pdfs_downloaded=0,
        indexed=False,
    )


@pytest.fixture
def scholar_html_fixture() -> bytes:
    """Load scholar page HTML fixture as bytes."""
    fixture_path = (
        Path(__file__).parent / "fixtures" / "scholar_page.html"
    )
    return fixture_path.read_text(encoding="utf-8").encode("utf-8")


@pytest.fixture
def isolated_environment(tmp_path: Path) -> dict[str, Path]:
    """Create isolated directories for end-to-end tests."""
    data_dir = tmp_path / "data"
    chroma_dir = tmp_path / "chroma"
    sessions_dir = data_dir / "sessions"

    data_dir.mkdir()
    chroma_dir.mkdir()
    sessions_dir.mkdir()

    return {
        "data_dir": data_dir,
        "chroma_dir": chroma_dir,
        "sessions_dir": sessions_dir,
    }


@pytest.fixture
def isolated_vectorstore(tmp_path: Path) -> VectorStore:
    """Create an isolated VectorStore instance for tests."""
    chroma_dir = tmp_path / "chroma_test"
    chroma_dir.mkdir()
    return VectorStore(persist_dir=chroma_dir)
