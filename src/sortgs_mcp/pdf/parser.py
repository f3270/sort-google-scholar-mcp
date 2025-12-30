"""PDF text extraction utilities."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import fitz

logger = logging.getLogger(__name__)


class PDFParser:
    """PDF text extraction using PyMuPDF.

    Note: Methods are synchronous. Use asyncio.to_thread() when calling from async context.
    """

    def extract_text(self, pdf_path: Path) -> str | None:
        """Extract text from a PDF.

        Returns:
            Extracted text if successful; None if PDF is empty, corrupted, or has no text.

        Raises:
            FileNotFoundError: If the PDF does not exist.
            PermissionError: If the PDF cannot be read.
        """
        path = Path(pdf_path)
        if not path.exists():
            logger.error("PDF not found: %s", path)
            raise FileNotFoundError(f"PDF not found: {path}")
        if not path.is_file():
            logger.error("PDF path is not a file: %s", path)
            raise FileNotFoundError(f"PDF path is not a file: {path}")
        if not os.access(path, os.R_OK):
            logger.error("Permission denied for PDF: %s", path)
            raise PermissionError(f"Permission denied for PDF: {path}")

        try:
            with fitz.open(path) as doc:
                pages_text: list[str] = []
                for page in doc:
                    pages_text.append(page.get_text("text"))
        except fitz.FileDataError as exc:
            logger.warning(
                "PDF appears corrupted or unreadable: %s (%s)",
                path,
                exc,
            )
            return None
        except PermissionError:
            logger.error("Permission denied when opening PDF: %s", path)
            raise
        except Exception as exc:
            logger.error(
                "Failed to parse PDF %s: %s",
                path,
                exc,
                exc_info=True,
            )
            return None

        full_text = "\n".join(pages_text).strip()
        if not full_text:
            logger.warning(
                "PDF is empty or contains no extractable text: %s",
                path,
                extra={"pdf_path": str(path), "reason": "empty_or_no_text"},
            )
            return None
        return full_text
