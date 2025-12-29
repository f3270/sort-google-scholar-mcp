import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import DownloadMetadata, PDFDownloadResult, Paper, SearchParams, SearchSession
from sortgs_mcp.tools import download as download_tool


def make_paper(rank: int, title: str, pdf_url: str | None = "https://example.com/paper.pdf") -> Paper:
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


class FakeDownloader:
    def __init__(self, result: PDFDownloadResult, max_concurrent: int | None = None) -> None:
        self.result = result
        self.max_concurrent = max_concurrent
        self.entered = False
        self.exited = False
        self.batch_args = None

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exited = True

    async def download_batch(self, papers, pdf_dir, session_id, project_root=None, force_redownload=False):
        self.batch_args = {
            "papers": papers,
            "pdf_dir": pdf_dir,
            "session_id": session_id,
            "project_root": project_root,
        }
        return self.result


def test_download_papers_basic(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = create_session(
        tmp_path,
        [make_paper(1, "Paper One"), make_paper(2, "Paper Two")],
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

    fake_downloader = FakeDownloader(result, max_concurrent=2)
    monkeypatch.setattr(download_tool, "PDFDownloader", lambda **kwargs: fake_downloader)

    response = asyncio.run(download_tool.download_papers(session_id, max_papers=2))
    assert response["downloaded"] == 1
    assert response["download_metadata"]

    saved = manager.load_session(session_id)
    assert saved.pdfs_downloaded == 1
    assert saved.download_metadata


def test_download_papers_no_pdfs(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = create_session(
        tmp_path,
        [make_paper(1, "Paper One", pdf_url=None)],
    )
    monkeypatch.setattr(download_tool, "session_manager", manager)

    response = asyncio.run(download_tool.download_papers(session_id, max_papers=1))
    assert response["downloaded"] == 0
    assert response["failed"] == 0


def test_download_papers_invalid_session(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(download_tool, "session_manager", SessionManager(tmp_path))

    with pytest.raises(FileNotFoundError):
        asyncio.run(download_tool.download_papers("missing-session"))


def test_download_papers_max_papers_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = create_session(
        tmp_path,
        [
            make_paper(1, "Paper One"),
            make_paper(2, "Paper Two"),
            make_paper(3, "Paper Three"),
        ],
    )
    monkeypatch.setattr(download_tool, "session_manager", manager)

    result = PDFDownloadResult(
        session_id=session_id,
        downloaded=0,
        skipped=0,
        failed=0,
    )
    fake_downloader = FakeDownloader(result)
    monkeypatch.setattr(download_tool, "PDFDownloader", lambda **kwargs: fake_downloader)

    asyncio.run(download_tool.download_papers(session_id, max_papers=2))
    assert fake_downloader.batch_args is not None
    assert len(fake_downloader.batch_args["papers"]) == 2


def test_download_papers_respects_max_concurrent(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "max_concurrent_downloads", 2)
    session_id, manager = create_session(
        tmp_path,
        [make_paper(1, "Paper One")],
    )
    monkeypatch.setattr(download_tool, "session_manager", manager)

    result = PDFDownloadResult(
        session_id=session_id,
        downloaded=0,
        skipped=0,
        failed=0,
    )
    fake_downloader = FakeDownloader(result, max_concurrent=2)

    def fake_factory(**kwargs):
        fake_downloader.max_concurrent = kwargs.get("max_concurrent")
        return fake_downloader

    monkeypatch.setattr(download_tool, "PDFDownloader", fake_factory)

    asyncio.run(download_tool.download_papers(session_id, max_papers=1))
    assert fake_downloader.max_concurrent == 2


def test_download_papers_uses_context_manager(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = create_session(
        tmp_path,
        [make_paper(1, "Paper One")],
    )
    monkeypatch.setattr(download_tool, "session_manager", manager)

    result = PDFDownloadResult(
        session_id=session_id,
        downloaded=0,
        skipped=0,
        failed=0,
    )
    fake_downloader = FakeDownloader(result)
    monkeypatch.setattr(download_tool, "PDFDownloader", lambda **kwargs: fake_downloader)

    asyncio.run(download_tool.download_papers(session_id, max_papers=1))
    assert fake_downloader.entered is True
    assert fake_downloader.exited is True
