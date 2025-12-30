"""PDF utilities for Sort Google Scholar MCP.

Usage from async context:
    chunks = await asyncio.to_thread(parse_and_chunk_pdf, pdf_path, paper, session_id)
"""

from __future__ import annotations

import logging
from pathlib import Path

from sortgs_mcp.models import Paper
from sortgs_mcp.pdf.chunker import TextChunker
from sortgs_mcp.pdf.downloader import PDFDownloader
from sortgs_mcp.pdf.parser import PDFParser

logger = logging.getLogger(__name__)

__all__ = ["PDFDownloader", "PDFParser", "TextChunker", "parse_and_chunk_pdf"]


def parse_and_chunk_pdf(
    pdf_path: Path,
    paper: Paper,
    session_id: str,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict] | None:
    """Parse PDF and create chunks with metadata.

    Returns:
        List of chunk dicts with 'text' and 'metadata' keys, or None if parsing fails.
        Chunks are ready for ChromaDB indexing.
    """
    parser = PDFParser()
    text = parser.extract_text(pdf_path)
    if text is None:
        logger.warning(
            "Skipping PDF with no text content: %s",
            pdf_path,
            extra={"pdf_path": str(pdf_path), "paper_rank": paper.rank},
        )
        return None

    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_paper(text, paper, session_id)
