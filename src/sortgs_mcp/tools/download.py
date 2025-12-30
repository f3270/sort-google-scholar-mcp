"""MCP tool for downloading PDFs from a saved session."""

import logging
from pathlib import Path

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import PDFDownloadResult
from sortgs_mcp.pdf import PDFDownloader
from sortgs_mcp.server import mcp

logger = logging.getLogger(__name__)
session_manager = SessionManager(settings.data_dir)


@mcp.tool()
async def download_papers(
    session_id: str,
    paper_indices: list[int] | None = None,
    max_papers: int = 10,
) -> dict:
    """Download PDFs for papers in a session."""
    if max_papers < 1:
        logger.error(
            "Invalid max_papers in download_papers",
            extra={"session_id": session_id, "max_papers": max_papers},
        )
        raise ValueError(
            "max_papers must be >= 1. "
            "Hint: Use a positive number like 5 or 10."
        )

    logger.info(
        "download_papers called",
        extra={
            "session_id": session_id,
            "max_papers": max_papers,
            "paper_indices": paper_indices,
        },
    )

    try:
        session = session_manager.load_session(session_id)
    except FileNotFoundError as exc:
        logger.error(
            "Session not found for download_papers",
            extra={"session_id": session_id},
        )
        raise ValueError(
            f"Session '{session_id}' not found. "
            "Hint: Use list_sessions tool to see all sessions."
        ) from exc

    papers_with_pdf = [paper for paper in session.papers if paper.pdf_url]

    if paper_indices:
        logger.info(
            "Filtering download_papers by indices",
            extra={
                "session_id": session_id,
                "paper_indices": paper_indices,
                "available_papers": len(papers_with_pdf),
            },
        )
        selected = []
        for idx in paper_indices:
            if idx < 0 or idx >= len(papers_with_pdf):
                logger.error(
                    "paper_indices out of range in download_papers",
                    extra={
                        "session_id": session_id,
                        "paper_index": idx,
                        "available_papers": len(papers_with_pdf),
                    },
                )
                raise ValueError(
                    f"paper_indices out of range: {idx}. "
                    "Hint: Indices must be within the available PDF list."
                )
            selected.append(papers_with_pdf[idx])
        papers_with_pdf = selected

    papers_with_pdf = papers_with_pdf[:max_papers]
    paper_ranks = [paper.rank for paper in papers_with_pdf]

    if not papers_with_pdf:
        logger.info(
            "No PDFs available to download",
            extra={"session_id": session_id, "available_papers": 0},
        )
        result = PDFDownloadResult(
            session_id=session_id,
            downloaded=0,
            skipped=0,
            failed=0,
        )
        return result.model_dump()

    pdf_dir = settings.pdf_download_dir(session_id)
    project_root = Path.cwd()

    try:
        async with PDFDownloader(
            max_concurrent=settings.max_concurrent_downloads
        ) as downloader:
            result = await downloader.download_batch(
                papers_with_pdf,
                pdf_dir,
                session_id,
                project_root=project_root,
            )
    except Exception as exc:
        logger.error(
            "download_papers failed",
            extra={
                "session_id": session_id,
                "max_papers": max_papers,
                "paper_ranks": paper_ranks,
            },
            exc_info=True,
        )
        raise RuntimeError(
            "download_papers failed. "
            "Hint: Check network connectivity or retry with fewer papers."
        ) from exc

    session.pdfs_downloaded += result.downloaded
    session.download_metadata = result.download_metadata
    session_manager.save_session(session, create_empty_csv=False)

    logger.info(
        "Downloaded PDFs for session",
        extra={
            "session_id": session_id,
            "downloaded": result.downloaded,
            "skipped": result.skipped,
            "failed": result.failed,
            "paper_ranks": paper_ranks,
        },
    )

    return result.model_dump()
