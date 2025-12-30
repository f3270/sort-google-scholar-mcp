import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

import sortgs_mcp.core.scholar as scholar_module
from sortgs_mcp.core.scholar import ScholarSearcher
from sortgs_mcp.models import SearchParams


def test_build_url_basic():
    params = SearchParams(keywords="machine learning", num_results=10)
    searcher = ScholarSearcher()
    url = searcher.build_url(params)
    assert "start=0" in url
    assert "q=machine+learning" in url
    assert "as_sdt=0,5" in url
    assert "web.archive.org" not in url


def test_build_url_with_years():
    params = SearchParams(
        keywords="test",
        num_results=10,
        start_year=2010,
        end_year=2020,
    )
    url = ScholarSearcher().build_url(params)
    assert "as_ylo=2010" in url
    assert "as_yhi=2020" in url


def test_build_url_with_languages():
    params = SearchParams(
        keywords="test", num_results=10, languages=["en", "es"]
    )
    url = ScholarSearcher().build_url(params)
    assert "lr=lang_en%7Clang_es" in url


def test_build_url_debug_mode():
    params = SearchParams(keywords="test", num_results=10, debug=True)
    url = ScholarSearcher().build_url(params)
    assert "web.archive.org" in url


@pytest.mark.asyncio
async def test_fetch_page_success(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    response = SimpleNamespace(content=b"<html>ok</html>")
    response.raise_for_status = lambda: None
    client = SimpleNamespace(get=AsyncMock(return_value=response))

    searcher = ScholarSearcher()
    content = await searcher._fetch_with_client(
        client, "https://example.com", debug_mode=False
    )
    assert content == b"<html>ok</html>"


@pytest.mark.asyncio
async def test_fetch_page_robot_detection(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    robot_html = b"not a robot"
    response = SimpleNamespace(content=robot_html)
    response.raise_for_status = lambda: None
    client = SimpleNamespace(get=AsyncMock(return_value=response))

    searcher = ScholarSearcher()
    monkeypatch.setattr(searcher, "fetch_with_selenium", lambda url: b"selenium")
    content = await searcher._fetch_with_client(
        client, "https://example.com", debug_mode=False
    )
    assert content == b"selenium"


@pytest.mark.asyncio
async def test_fetch_page_http_error_debug(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    async def _raise(*args, **kwargs):
        raise httpx.HTTPError("timeout")

    client = SimpleNamespace(get=_raise)
    searcher = ScholarSearcher(debug=True)
    content = await searcher._fetch_with_client(
        client, "https://example.com", debug_mode=True
    )
    assert content == scholar_module.DEBUG_SAMPLE_HTML


def _make_result(idx: int, citations: int, year: int) -> dict:
    return {
        "title": f"Paper {idx}",
        "authors": "A Author",
        "citations": citations,
        "year": year,
        "publisher": "Publisher",
        "venue": "Venue",
        "content_snippet": "Snippet",
        "source_url": f"https://example.com/{idx}",
        "pdf_url": None,
    }


@pytest.mark.asyncio
async def test_search_sorting_by_citations(monkeypatch):
    params = SearchParams(keywords="test", num_results=10, sort_by="Citations")

    async def fake_fetch_page(self, url, debug_mode=False):
        return b"<html></html>"

    def fake_results():
        return [
            _make_result(1, 10, 2020),
            _make_result(2, 5, 2020),
            _make_result(3, 7, 2019),
            _make_result(4, 1, 2021),
            _make_result(5, 9, 2018),
            _make_result(6, 2, 2017),
            _make_result(7, 3, 2016),
            _make_result(8, 4, 2015),
            _make_result(9, 6, 2014),
            _make_result(10, 8, 2013),
        ]

    monkeypatch.setattr(ScholarSearcher, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(
        scholar_module,
        "parse_google_scholar_page",
        lambda html: fake_results(),
    )

    searcher = ScholarSearcher()
    results = await searcher.search(params)
    assert results[0].citations == 10
    assert results[0].rank == 1


@pytest.mark.asyncio
async def test_search_sorting_by_cit_per_year(monkeypatch):
    params = SearchParams(
        keywords="test",
        num_results=10,
        sort_by="cit/year",
        end_year=2024,
    )

    async def fake_fetch_page(self, url, debug_mode=False):
        return b"<html></html>"

    def fake_results():
        return [
            _make_result(1, 100, 2014),
            _make_result(2, 50, 2024),
            _make_result(3, 60, 2020),
            _make_result(4, 10, 2023),
            _make_result(5, 90, 2015),
            _make_result(6, 5, 2024),
            _make_result(7, 30, 2022),
            _make_result(8, 20, 2024),
            _make_result(9, 70, 2018),
            _make_result(10, 40, 2019),
        ]

    monkeypatch.setattr(ScholarSearcher, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(
        scholar_module,
        "parse_google_scholar_page",
        lambda html: fake_results(),
    )

    searcher = ScholarSearcher()
    results = await searcher.search(params)
    assert results[0].title == "Paper 2"
    assert results[0].cit_per_year >= results[1].cit_per_year


@pytest.mark.asyncio
async def test_search_pagination_multiple_pages(monkeypatch):
    params = SearchParams(keywords="test", num_results=20, sort_by="Citations")

    async def fake_fetch_page(self, url, debug_mode=False):
        return b"<html></html>"

    monkeypatch.setattr(ScholarSearcher, "fetch_page", fake_fetch_page)

    call_count = {"count": 0}

    def fake_parser(html):
        call_count["count"] += 1
        base = (call_count["count"] - 1) * 10
        return [
            _make_result(base + idx + 1, 10 - idx, 2020)
            for idx in range(10)
        ]

    monkeypatch.setattr(scholar_module, "parse_google_scholar_page", fake_parser)

    searcher = ScholarSearcher()
    results = await searcher.search(params)
    assert len(results) == 20
    assert results[0].rank == 1


@pytest.mark.asyncio
async def test_search_full_workflow(monkeypatch):
    params = SearchParams(keywords="test", num_results=10, sort_by="Citations")

    async def fake_fetch_page(self, url, debug_mode=False):
        return b"<html></html>"

    monkeypatch.setattr(ScholarSearcher, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(
        scholar_module,
        "parse_google_scholar_page",
        lambda html: [_make_result(idx + 1, 7 + idx, 2022) for idx in range(10)],
    )

    searcher = ScholarSearcher()
    results = await searcher.search(params)
    assert len(results) == 10
    assert results[0].title == "Paper 10"
