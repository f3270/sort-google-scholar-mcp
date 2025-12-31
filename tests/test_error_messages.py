import asyncio
import json
from pathlib import Path

import pytest

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import Paper, SearchParams, SearchSession
from sortgs_mcp.tools import download as download_tool
from sortgs_mcp.tools import index as index_tool
from sortgs_mcp.tools import query as query_tool
from sortgs_mcp.tools import search as search_tool


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
    tmp_path: Path, indexed: bool = False
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
        papers=[_make_paper(1, "Paper One")],
        indexed=indexed,
    )
    manager = SessionManager(tmp_path)
    manager.save_session(session)
    return session_id, manager


def test_search_papers_empty_keywords_has_hint():
    with pytest.raises(ValueError, match="Hint:"):
        asyncio.run(search_tool.search_papers(keywords="  "))


def test_download_papers_missing_session_has_hint(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(download_tool, "session_manager", SessionManager(tmp_path))

    with pytest.raises(ValueError, match="Hint:"):
        asyncio.run(download_tool.download_papers("missing-session"))


def test_index_papers_no_pdfs_has_hint(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = _create_session(tmp_path)
    monkeypatch.setattr(index_tool, "session_manager", manager)

    with pytest.raises(RuntimeError, match="Hint:"):
        asyncio.run(index_tool.index_papers(session_id))


def test_query_papers_missing_session_has_hint(tmp_path, monkeypatch):
    manager = SessionManager(tmp_path)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    with pytest.raises(ValueError, match="Hint:"):
        asyncio.run(query_tool.query_papers("question", session_id="missing"))


def test_query_papers_not_indexed_has_hint(tmp_path, monkeypatch):
    manager = SessionManager(tmp_path)
    session = SearchSession(
        session_id="session-1",
        params=SearchParams(keywords="test", num_results=10, sort_by="Citations"),
        papers=[],
        indexed=False,
    )
    manager.save_session(session)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    with pytest.raises(RuntimeError, match="Hint:"):
        asyncio.run(query_tool.query_papers("question", session_id="session-1"))


def test_list_sessions_returns_metadata(tmp_path, monkeypatch):
    session_id, manager = _create_session(tmp_path, indexed=True)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    response = asyncio.run(query_tool.list_sessions())
    assert response["sessions"][0]["session_id"] == session_id
    for key in [
        "session_id",
        "keywords",
        "created_at",
        "papers_count",
        "pdfs_downloaded",
        "indexed",
    ]:
        assert key in response["sessions"][0]
    json.dumps(response)
