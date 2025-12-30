"""Text chunking utilities for RAG indexing."""

from __future__ import annotations

import logging
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from sortgs_mcp.models import Paper

logger = logging.getLogger(__name__)


class TextChunker:
    """Text chunking for RAG indexing.

    Chunks are returned as dicts compatible with ChromaDB metadata schema.
    Note: Methods are synchronous. Use asyncio.to_thread() when calling from async context.
    """

    REQUIRED_METADATA_FIELDS = {
        "session_id",
        "paper_title",
        "paper_authors",
        "paper_year",
        "paper_citations",
        "paper_rank",
        "source_url",
        "chunk_index",
        "total_chunks",
    }

    def __init__(
        self,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
        )

    def validate_chunk_metadata(self, chunk: dict) -> bool:
        """Validate chunk dict against the required metadata schema."""
        if "text" not in chunk or "metadata" not in chunk:
            return False

        text = chunk.get("text", "")
        if not isinstance(text, str) or not text.strip():
            return False

        metadata = chunk.get("metadata", {})
        if not isinstance(metadata, dict):
            return False

        if not self.REQUIRED_METADATA_FIELDS.issubset(metadata.keys()):
            return False

        session_id = metadata.get("session_id")
        if not isinstance(session_id, str):
            return False
        try:
            uuid.UUID(session_id)
        except (ValueError, TypeError, AttributeError):
            return False

        if not isinstance(metadata.get("paper_title"), str):
            return False
        if not isinstance(metadata.get("paper_authors"), str):
            return False
        if not isinstance(metadata.get("source_url"), str):
            return False

        paper_year = metadata.get("paper_year")
        paper_citations = metadata.get("paper_citations")
        paper_rank = metadata.get("paper_rank")
        chunk_index = metadata.get("chunk_index")
        total_chunks = metadata.get("total_chunks")

        if not isinstance(paper_year, int) or paper_year < 1900:
            return False
        if not isinstance(paper_citations, int) or paper_citations < 0:
            return False
        if not isinstance(paper_rank, int) or paper_rank < 0:
            return False
        if not isinstance(chunk_index, int) or chunk_index < 0:
            return False
        if not isinstance(total_chunks, int) or total_chunks <= 0:
            return False
        if chunk_index >= total_chunks:
            return False

        return True

    def chunk_paper(self, text: str, paper: Paper, session_id: str) -> list[dict]:
        """Split paper text into chunks with metadata."""
        if not text or not text.strip():
            raise ValueError("Text is empty; cannot create chunks.")

        chunks = self._splitter.split_text(text)
        if not chunks:
            return []

        total_chunks = len(chunks)
        chunk_dicts: list[dict] = []

        for idx, chunk_text in enumerate(chunks):
            metadata = {
                "session_id": session_id,
                "paper_title": paper.title,
                "paper_authors": paper.authors,
                "paper_year": paper.year,
                "paper_citations": paper.citations,
                "paper_rank": paper.rank,
                "source_url": paper.source_url,
                "chunk_index": idx,
                "total_chunks": total_chunks,
            }
            chunk_dict = {
                "text": chunk_text,
                "metadata": metadata,
            }
            if not self.validate_chunk_metadata(chunk_dict):
                logger.error("Chunk metadata validation failed for %s", paper.title)
                raise ValueError("Chunk metadata validation failed.")
            chunk_dicts.append(chunk_dict)

        return chunk_dicts
