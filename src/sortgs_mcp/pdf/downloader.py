"""Async PDF downloader with validation and concurrency control."""

from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime
from pathlib import Path

try:
    import aiofiles
    from aiofiles import ospath
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal test envs
    class _AsyncFile:
        def __init__(self, path: Path, mode: str) -> None:
            self._path = path
            self._mode = mode
            self._handle = None

        async def __aenter__(self):
            self._handle = open(self._path, self._mode)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
            if self._handle:
                self._handle.close()
                self._handle = None

        async def read(self, size: int = -1) -> bytes:
            return self._handle.read(size)

        async def write(self, data: bytes) -> int:
            return self._handle.write(data)

    class _AiofilesModule:
        @staticmethod
        def open(path: Path, mode: str) -> _AsyncFile:
            return _AsyncFile(path, mode)

    class _OsPathModule:
        @staticmethod
        async def exists(path: Path) -> bool:
            return os.path.exists(path)

        @staticmethod
        async def getsize(path: Path) -> int:
            return os.path.getsize(path)

    aiofiles = _AiofilesModule()
    ospath = _OsPathModule()
import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from sortgs_mcp.config import settings
from sortgs_mcp.models import DownloadMetadata, PDFDownloadResult, Paper

logger = logging.getLogger(__name__)

_PDF_MAGIC = b"%PDF"


def sanitize_filename(title: str, rank: int) -> str:
    """Create a safe filename for a paper PDF."""
    safe_title = re.sub(r"[^\w\s-]", "", title)
    safe_title = re.sub(r"\s+", "_", safe_title).strip("_")
    safe_title = safe_title[:100] if safe_title else "untitled"
    return f"paper_{rank:03d}_{safe_title}.pdf"


def _normalize_pdf_path(path: Path, project_root: Path) -> str:
    """Return a project-root-relative path string for stored metadata."""
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(project_root)
    except ValueError:
        relative = Path(os.path.relpath(resolved, project_root))
    return relative.as_posix()


class PDFDownloader:
    """Async PDF downloader with retry, validation, and concurrency control."""

    def __init__(
        self,
        *,
        max_concurrent: int | None = None,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.max_concurrent = max_concurrent or settings.max_concurrent_downloads
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "PDFDownloader":
        self._client = self._make_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _make_client(self) -> httpx.AsyncClient:
        """Create a configured AsyncClient."""
        return httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
            follow_redirects=True,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPError)),
    )
    async def _fetch_pdf(self, url: str) -> httpx.Response:
        """Fetch a PDF with retry using the configured client."""
        if self._client is None:
            async with self._make_client() as client:
                return await client.get(url)
        return await self._client.get(url)

    @staticmethod
    def _is_valid_pdf_header(content: bytes) -> bool:
        """Validate PDF magic bytes in the first few bytes."""
        return content[:10].lstrip().startswith(_PDF_MAGIC)

    async def _existing_pdf_metadata(
        self,
        filepath: Path,
        paper: Paper,
        project_root: Path,
    ) -> DownloadMetadata | None:
        if not await ospath.exists(filepath):
            return None

        size = await ospath.getsize(filepath)
        if size <= 0:
            return None

        async with aiofiles.open(filepath, "rb") as handle:
            header = await handle.read(10)
        if not self._is_valid_pdf_header(header):
            return None

        return DownloadMetadata(
            rank=paper.rank,
            title=paper.title,
            pdf_path=_normalize_pdf_path(filepath, project_root),
            file_size_bytes=size,
            download_timestamp=datetime.now(),
            status="skipped",
        )

    async def download_single(
        self,
        url: str,
        filepath: Path,
        paper: Paper,
        project_root: Path,
        *,
        force_redownload: bool = False,
    ) -> tuple[str, str | None, DownloadMetadata | None]:
        """Download a single PDF and return status, error, and metadata."""
        if not force_redownload:
            existing_metadata = await self._existing_pdf_metadata(filepath, paper, project_root)
            if existing_metadata:
                return "skipped", None, existing_metadata

        try:
            response = await self._fetch_pdf(url)
            response.raise_for_status()
            content = response.content

            if not self._is_valid_pdf_header(content):
                raise ValueError(
                    "Magic bytes validation failed - content is not a valid PDF"
                )

            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" not in content_type:
                logger.warning(
                    "Content-Type is not PDF for %s (got %s), but magic bytes valid",
                    url,
                    content_type or "missing",
                )

            filepath.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(filepath, "wb") as handle:
                await handle.write(content)

            metadata = DownloadMetadata(
                rank=paper.rank,
                title=paper.title,
                pdf_path=_normalize_pdf_path(filepath, project_root),
                file_size_bytes=len(content),
                download_timestamp=datetime.now(),
                status="downloaded",
            )
            return "downloaded", None, metadata
        except httpx.HTTPStatusError as exc:
            reason = exc.response.reason_phrase or "HTTP error"
            return "failed", f"{exc.response.status_code} {reason}", None
        except (httpx.HTTPError, ValueError) as exc:
            return "failed", str(exc), None
        except Exception as exc:
            logger.error("Unexpected error downloading %s: %s", url, exc, exc_info=True)
            return "failed", f"Unexpected error: {exc}", None

    async def _download_with_semaphore(
        self,
        paper: Paper,
        filepath: Path,
        project_root: Path,
        *,
        force_redownload: bool = False,
    ) -> dict:
        async with self.semaphore:
            status, error, metadata = await self.download_single(
                paper.pdf_url or "",
                filepath,
                paper,
                project_root,
                force_redownload=force_redownload,
            )
            return {
                "rank": paper.rank,
                "title": paper.title,
                "status": status,
                "error": error,
                "metadata": metadata,
            }

    async def download_batch(
        self,
        papers: list[Paper],
        pdf_dir: Path,
        session_id: str,
        *,
        project_root: Path | None = None,
        force_redownload: bool = False,
    ) -> PDFDownloadResult:
        """Download multiple PDFs with concurrency control."""
        result = PDFDownloadResult(
            session_id=session_id,
            downloaded=0,
            skipped=0,
            failed=0,
        )

        project_root = (project_root or Path.cwd()).resolve()
        pdf_dir.mkdir(parents=True, exist_ok=True)

        tasks = []
        for paper in papers:
            if not paper.pdf_url:
                continue
            filename = sanitize_filename(paper.title, paper.rank)
            filepath = pdf_dir / filename
            tasks.append(
                asyncio.create_task(
                    self._download_with_semaphore(
                        paper,
                        filepath,
                        project_root,
                        force_redownload=force_redownload,
                    )
                )
            )

        if not tasks:
            return result

        try:
            outcomes = await asyncio.gather(*tasks)
        except Exception as exc:
            logger.error("download_batch failed before gather: %s", exc, exc_info=True)
            result.error = str(exc)
            return result

        metadata_list: list[DownloadMetadata] = []
        failed_papers: list[dict] = []

        for outcome in outcomes:
            status = outcome["status"]
            if status == "downloaded":
                result.downloaded += 1
            elif status == "skipped":
                result.skipped += 1
            else:
                result.failed += 1

            if outcome["metadata"]:
                metadata_list.append(outcome["metadata"])
            elif status == "failed":
                failed_papers.append(
                    {
                        "rank": outcome["rank"],
                        "title": outcome["title"],
                        "reason": outcome["error"] or "Unknown error",
                    }
                )

        metadata_list.sort(key=lambda item: item.rank)
        failed_papers.sort(key=lambda item: item["rank"])

        result.download_metadata = metadata_list
        result.pdf_paths = [meta.pdf_path for meta in metadata_list]
        result.failed_papers = failed_papers
        return result
