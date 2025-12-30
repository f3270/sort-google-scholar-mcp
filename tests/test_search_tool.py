import asyncio

import httpx
import pytest

from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import SearchParams, SearchSession
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


def test_search_papers_success(tmp_path, sample_papers, monkeypatch):
    manager = SessionManager(tmp_path)
    monkeypatch.setattr(search_tool, "session_manager", manager)
    monkeypatch.setattr(search_tool.settings, "data_dir", tmp_path)

    monkeypatch.setattr(
        "sortgs_mcp.core.scholar.ScholarSearcher",
        lambda debug=False: FakeScholarSearcher(sample_papers),
    )

    response = asyncio.run(
        search_tool.search_papers(
            keywords="transformers",
            num_results=10,
            sort_by="Citations",
            debug=True,
        )
    )

    assert response["papers_found"] == len(sample_papers)
    session = manager.load_session(response["session_id"])
    assert session.papers_count == len(sample_papers)


def test_search_papers_empty_keywords():
    with pytest.raises(ValueError, match="Invalid parameters"):
        asyncio.run(search_tool.search_papers(keywords="  "))


def test_search_papers_http_error(tmp_path, monkeypatch):
    manager = SessionManager(tmp_path)
    monkeypatch.setattr(search_tool, "session_manager", manager)

    class FakeErrorSearcher:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

        async def search(self, params):
            raise httpx.HTTPError("boom")

    monkeypatch.setattr(
        "sortgs_mcp.core.scholar.ScholarSearcher",
        lambda debug=False: FakeErrorSearcher(),
    )

    with pytest.raises(RuntimeError, match="Failed to fetch results"):
        asyncio.run(
            search_tool.search_papers(
                keywords="transformers", num_results=10, debug=False
            )
        )


def test_generate_search_keywords_success(monkeypatch):
    monkeypatch.setattr(search_tool.settings, "openai_api_key", "test")

    async def fake_generate_keywords(query, num_variations):
        return ["kw1", "kw2"]

    class FakeClient:
        async def generate_keywords(self, query, num_variations):
            return await fake_generate_keywords(query, num_variations)

    monkeypatch.setattr(search_tool, "OpenAIClient", lambda **kwargs: FakeClient())

    response = asyncio.run(
        search_tool.generate_search_keywords("test query", num_variations=2)
    )
    assert response["keywords"] == ["kw1", "kw2"]


def test_generate_search_keywords_invalid_args():
    with pytest.raises(ValueError):
        asyncio.run(search_tool.generate_search_keywords("  "))
    with pytest.raises(ValueError):
        asyncio.run(search_tool.generate_search_keywords("test", num_variations=0))
