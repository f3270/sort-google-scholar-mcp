import json

import pytest
from pydantic import ValidationError

from sortgs_mcp.models import (
    DownloadMetadata,
    Paper,
    PDFDownloadResult,
    QueryResult,
    QuerySource,
    SearchParams,
    SearchSession,
)


def test_paper_creation_valid(sample_paper):
    assert sample_paper.title == "Attention Is All You Need"
    assert sample_paper.citations == 50000
    assert sample_paper.pdf_url is not None


def test_paper_validation_missing_required_fields():
    with pytest.raises(ValidationError):
        Paper(
            rank=1,
            title="Missing authors",
            citations=1,
            year=2020,
            publisher="Publisher",
            venue="Venue",
            content_snippet="Snippet",
            source_url="https://example.com",
            cit_per_year=1,
        )


def test_search_params_defaults():
    params = SearchParams(keywords="transformers")
    assert params.num_results == 100
    assert params.sort_by == "Citations"
    assert params.start_year is None
    assert params.debug is False


def test_search_params_year_validation():
    with pytest.raises(ValidationError, match="start_year"):
        SearchParams(
            keywords="test",
            start_year=2025,
            end_year=2020,
        )


def test_search_params_sort_by_literal():
    with pytest.raises(ValidationError):
        SearchParams(keywords="test", sort_by="invalid")


def test_search_params_num_results_bounds():
    with pytest.raises(ValidationError):
        SearchParams(keywords="test", num_results=5)
    with pytest.raises(ValidationError):
        SearchParams(keywords="test", num_results=1001)


def test_search_session_serialization(sample_search_params, sample_papers):
    session = SearchSession(
        session_id="session-1",
        params=sample_search_params,
        papers=sample_papers,
        papers_count=len(sample_papers),
        pdfs_downloaded=1,
        indexed=True,
    )
    payload = session.model_dump_json()
    loaded = SearchSession.model_validate_json(payload)
    assert loaded.session_id == session.session_id
    assert loaded.papers_count == 2
    assert loaded.indexed is True


def test_search_session_json_roundtrip(sample_search_params):
    session = SearchSession(
        session_id="session-2",
        params=sample_search_params,
    )
    data = json.loads(session.model_dump_json())
    restored = SearchSession.model_validate(data)
    assert restored.session_id == "session-2"
    assert restored.params.keywords == sample_search_params.keywords


def test_pdf_download_result_counts():
    metadata = DownloadMetadata(
        rank=1,
        title="Test Paper",
        pdf_path="data/sessions/x/pdfs/paper_001_test.pdf",
        file_size_bytes=123,
    )
    result = PDFDownloadResult(
        session_id="session-1",
        downloaded=1,
        skipped=0,
        failed=0,
        pdf_paths=[metadata.pdf_path],
        download_metadata=[metadata],
    )
    assert result.downloaded == 1
    assert result.failed == 0
    assert result.download_metadata


def test_query_result_with_sources():
    source = QuerySource(
        paper_title="Paper 1",
        chunk_text="Relevant chunk",
        relevance_score=0.9,
        metadata={"paper_rank": 1},
    )
    result = QueryResult(
        question="What is attention?",
        answer="Self-attention is...",
        sources=[source],
        session_id="session-1",
    )
    assert result.sources[0].metadata["paper_rank"] == 1
    assert result.session_id == "session-1"
