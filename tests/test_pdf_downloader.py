import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from sortgs_mcp.models import DownloadMetadata, Paper
from sortgs_mcp.pdf.downloader import (
    PDFDownloader,
    _normalize_pdf_path,
    sanitize_filename,
)
from tests.fixtures.pdf_responses import (
    mock_404_response,
    mock_html_response,
    mock_pdf_no_content_type,
    mock_pdf_response,
)


class MockAsyncClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.closed = False
        self.calls = 0

    async def get(self, url):
        self.calls += 1
        if self._responses:
            return self._responses.pop(0)
        raise AssertionError("No mock responses left")

    async def aclose(self):
        self.closed = True


def make_paper(
    rank: int, title: str, pdf_url: str | None = "https://example.com/paper.pdf"
) -> Paper:
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


def test_sanitize_filename():
    filename = sanitize_filename("A Paper: Title? With *Chars*", 1)
    assert filename.startswith("paper_001_")
    assert ":" not in filename
    assert "*" not in filename
    assert len(filename) <= 120


def test_context_manager_lifecycle():
    downloader = PDFDownloader(max_concurrent=1)
    client = MockAsyncClient([])
    downloader._make_client = lambda: client

    async def run():
        async with downloader:
            assert downloader._client is client
        assert client.closed is True

    asyncio.run(run())


def test_download_single_success(tmp_path, mock_pdf_response):
    downloader = PDFDownloader(max_concurrent=1)
    downloader._client = MockAsyncClient([mock_pdf_response])
    paper = make_paper(1, "Paper One")
    filepath = tmp_path / "paper.pdf"

    async def run():
        status, error, metadata = await downloader.download_single(
            paper.pdf_url or "",
            filepath,
            paper,
            tmp_path,
        )
        return status, error, metadata

    status, error, metadata = asyncio.run(run())
    assert status == "downloaded"
    assert error is None
    assert metadata is not None
    assert metadata.file_size_bytes > 0
    assert metadata.status == "downloaded"


def test_download_single_invalid_magic_bytes(tmp_path, mock_html_response):
    downloader = PDFDownloader(max_concurrent=1)
    downloader._client = MockAsyncClient([mock_html_response])
    paper = make_paper(1, "Paper One")
    filepath = tmp_path / "paper.pdf"

    async def run():
        return await downloader.download_single(
            paper.pdf_url or "",
            filepath,
            paper,
            tmp_path,
        )

    status, error, metadata = asyncio.run(run())
    assert status == "failed"
    assert "Magic bytes validation failed" in (error or "")
    assert metadata is None


def test_download_single_http_error(tmp_path, mock_404_response):
    downloader = PDFDownloader(max_concurrent=1)
    downloader._client = MockAsyncClient([mock_404_response])
    paper = make_paper(1, "Paper One")
    filepath = tmp_path / "paper.pdf"

    async def run():
        return await downloader.download_single(
            paper.pdf_url or "",
            filepath,
            paper,
            tmp_path,
        )

    status, error, metadata = asyncio.run(run())
    assert status == "failed"
    assert "404" in (error or "")
    assert metadata is None


def test_download_single_missing_content_type(
    tmp_path, mock_pdf_no_content_type, caplog
):
    downloader = PDFDownloader(max_concurrent=1)
    downloader._client = MockAsyncClient([mock_pdf_no_content_type])
    paper = make_paper(1, "Paper One")
    filepath = tmp_path / "paper.pdf"

    async def run():
        return await downloader.download_single(
            paper.pdf_url or "",
            filepath,
            paper,
            tmp_path,
        )

    with caplog.at_level("WARNING"):
        status, error, metadata = asyncio.run(run())
    assert status == "downloaded"
    assert error is None
    assert metadata is not None


def test_download_batch_all_success(tmp_path, mock_pdf_response):
    downloader = PDFDownloader(max_concurrent=2)
    downloader._client = MockAsyncClient(
        [mock_pdf_response, mock_pdf_response, mock_pdf_response]
    )
    papers = [
        make_paper(1, "Paper One"),
        make_paper(2, "Paper Two"),
        make_paper(3, "Paper Three"),
    ]

    async def run():
        return await downloader.download_batch(
            papers,
            tmp_path,
            "session-id",
            project_root=tmp_path,
        )

    result = asyncio.run(run())
    assert result.downloaded == 3
    assert result.failed == 0
    assert result.skipped == 0
    assert len(result.download_metadata) == 3
    assert len(result.pdf_paths) == 3
    assert all(not Path(path).is_absolute() for path in result.pdf_paths)


def test_download_batch_mixed(
    tmp_path, mock_pdf_response, mock_404_response, mock_html_response
):
    downloader = PDFDownloader(max_concurrent=2)
    downloader._client = MockAsyncClient(
        [mock_pdf_response, mock_404_response, mock_html_response]
    )
    papers = [
        make_paper(1, "Paper One"),
        make_paper(2, "Paper Two"),
        make_paper(3, "Paper Three"),
    ]

    async def run():
        return await downloader.download_batch(
            papers,
            tmp_path,
            "session-id",
            project_root=tmp_path,
        )

    result = asyncio.run(run())
    assert result.downloaded == 1
    assert result.failed == 2
    assert len(result.failed_papers) == 2


def test_download_batch_semaphore(tmp_path):
    downloader = PDFDownloader(max_concurrent=2)
    papers = [make_paper(i + 1, f"Paper {i + 1}") for i in range(5)]
    active = 0
    max_active = 0

    async def fake_download_single(
        self, url, filepath, paper, project_root, *, force_redownload=False
    ):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        metadata = DownloadMetadata(
            rank=paper.rank,
            title=paper.title,
            pdf_path=_normalize_pdf_path(filepath, project_root),
            file_size_bytes=10,
            download_timestamp=datetime.now(),
            status="downloaded",
        )
        return "downloaded", None, metadata

    downloader.download_single = fake_download_single.__get__(downloader, PDFDownloader)

    async def run():
        return await downloader.download_batch(
            papers,
            tmp_path,
            "session-id",
            project_root=tmp_path,
        )

    asyncio.run(run())
    assert max_active <= 2


def test_download_batch_idempotence_skip(tmp_path, mock_pdf_response):
    downloader = PDFDownloader(max_concurrent=1)
    downloader._client = MockAsyncClient([mock_pdf_response])
    paper = make_paper(1, "Paper One")
    filename = sanitize_filename(paper.title, paper.rank)
    filepath = tmp_path / filename
    filepath.write_bytes(b"%PDF-1.4\n%cached pdf")

    async def run():
        return await downloader.download_batch(
            [paper],
            tmp_path,
            "session-id",
            project_root=tmp_path,
        )

    result = asyncio.run(run())
    assert result.downloaded == 0
    assert result.skipped == 1
    assert result.download_metadata
    assert result.download_metadata[0].status == "skipped"
