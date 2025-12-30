"""MCP tool for indexing PDFs into ChromaDB."""

from __future__ import annotations

import asyncio
import logging
import re
import time
from pathlib import Path

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import IndexingResult
from sortgs_mcp.pdf import parse_and_chunk_pdf
from sortgs_mcp.rag import VectorStore, get_embedding_service
from sortgs_mcp.server import mcp

logger = logging.getLogger(__name__)
session_manager = SessionManager(settings.data_dir)
_PDF_RANK_PATTERN = re.compile(r"paper_(\d{3})_")


def _validate_index_params(
    chunk_size: int, chunk_overlap: int, max_chunks: int
) -> None:
    """Validate indexing settings for chunk sizes and limits."""
    if not 100 <= chunk_size <= 5000:
        logger.error(
            "Invalid chunk_size in index_papers",
            extra={"chunk_size": chunk_size},
        )
        raise ValueError(
            "chunk_size must be between 100 and 5000. "
            "Hint: Try 1000 for general-purpose indexing."
        )
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        logger.error(
            "Invalid chunk_overlap in index_papers",
            extra={"chunk_overlap": chunk_overlap, "chunk_size": chunk_size},
        )
        raise ValueError(
            "chunk_overlap must be >= 0 and < chunk_size. "
            "Hint: Try 200 for moderate overlap."
        )
    if max_chunks < 100:
        logger.error(
            "Invalid max_chunks in index_papers",
            extra={"max_chunks": max_chunks},
        )
        raise ValueError(
            "max_chunks must be >= 100. "
            "Hint: Use a higher limit for large sessions."
        )


def _find_paper_rank(pdf_path: Path) -> int:
    """Extract the paper rank from a PDF filename."""
    match = _PDF_RANK_PATTERN.search(pdf_path.name)
    if not match:
        raise ValueError(
            f"Unable to extract rank from {pdf_path.name}. "
            "Hint: Expected filename format 'paper_###_*.pdf'."
        )
    return int(match.group(1))


@mcp.tool()
async def index_papers(
    session_id: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    max_chunks: int | None = None,
) -> dict:
    """Index PDFs from a session into ChromaDB."""
    resolved_chunk_size = (
        settings.chunk_size if chunk_size is None else chunk_size
    )
    resolved_chunk_overlap = (
        settings.chunk_overlap if chunk_overlap is None else chunk_overlap
    )
    resolved_max_chunks = (
        settings.max_chunks_per_session if max_chunks is None else max_chunks
    )
    _validate_index_params(
        resolved_chunk_size, resolved_chunk_overlap, resolved_max_chunks
    )

    logger.info(
        "index_papers called",
        extra={
            "session_id": session_id,
            "chunk_size": resolved_chunk_size,
            "chunk_overlap": resolved_chunk_overlap,
            "max_chunks": resolved_max_chunks,
        },
    )

    try:
        session = session_manager.load_session(session_id)
    except FileNotFoundError as exc:
        logger.error(
            "Session not found for index_papers",
            extra={"session_id": session_id},
        )
        raise ValueError(
            f"Session '{session_id}' not found. "
            "Hint: Use list_sessions tool to see all sessions."
        ) from exc
    pdf_dir = settings.pdf_download_dir(session_id)
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(
            "No PDFs found for index_papers",
            extra={"session_id": session_id, "pdf_dir": str(pdf_dir)},
        )
        raise RuntimeError(
            "No PDFs found. Run download_papers first. "
            "Hint: Use download_papers to fetch PDFs before indexing."
        )

    paper_by_rank = {paper.rank: paper for paper in session.papers}
    all_chunks: list[dict] = []
    failed_papers: list[str] = []
    papers_indexed = 0
    start_time = time.monotonic()

    for pdf_path in pdf_files:
        paper = None
        rank = None
        try:
            rank = _find_paper_rank(pdf_path)
            paper = paper_by_rank.get(rank)
            if paper is None:
                raise ValueError(
                    f"No paper found for rank {rank}. "
                    "Hint: Ensure PDF filenames match the search session ranks."
                )

            logger.info(
                "Indexing PDF",
                extra={
                    "session_id": session_id,
                    "pdf_path": str(pdf_path),
                    "paper_rank": rank,
                },
            )
            chunks = await asyncio.to_thread(
                parse_and_chunk_pdf,
                pdf_path,
                paper,
                session_id,
                chunk_size=resolved_chunk_size,
                chunk_overlap=resolved_chunk_overlap,
            )
            if not chunks:
                failed_papers.append(paper.title)
                continue

            remaining = resolved_max_chunks - len(all_chunks)
            if remaining <= 0:
                logger.warning(
                    "Reached max_chunks limit",
                    extra={
                        "session_id": session_id,
                        "max_chunks": resolved_max_chunks,
                        "chunks_indexed": len(all_chunks),
                        "paper_rank": rank,
                    },
                )
                break
            if len(chunks) > remaining:
                all_chunks.extend(chunks[:remaining])
                logger.warning(
                    "Reached max_chunks limit",
                    extra={
                        "session_id": session_id,
                        "max_chunks": resolved_max_chunks,
                        "chunks_indexed": len(all_chunks),
                        "paper_rank": rank,
                    },
                )
                papers_indexed += 1
                break

            all_chunks.extend(chunks)
            papers_indexed += 1
        except Exception as exc:
            name = paper.title if paper else pdf_path.name
            logger.error(
                "Failed to parse PDF",
                extra={
                    "session_id": session_id,
                    "pdf_path": str(pdf_path),
                    "paper_rank": rank,
                    "error": str(exc),
                },
            )
            failed_papers.append(name)

    embedder = get_embedding_service(settings.embedding_model)
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings: list[list[float]]
    if texts:
        embeddings = await asyncio.to_thread(
            embedder.embed_texts,
            texts,
            batch_size=settings.embedding_batch_size,
        )
    else:
        embeddings = []

    vectorstore = VectorStore(
        settings.chroma_persist_dir,
        embedding_dim=embedder.embedding_dim,
        distance_metric="cosine",
        model_name=embedder.model_name,
    )
    indexed_count = vectorstore.add_documents(session_id, all_chunks, embeddings)

    session.indexed = True
    session_manager.save_session(session, create_empty_csv=False)

    elapsed = time.monotonic() - start_time
    logger.info(
        "index_papers completed",
        extra={
            "session_id": session_id,
            "papers_indexed": papers_indexed,
            "chunks_created": indexed_count,
            "failed_papers": len(failed_papers),
            "indexing_time_sec": round(elapsed, 2),
        },
    )
    result = IndexingResult(
        session_id=session_id,
        papers_indexed=papers_indexed,
        chunks_created=indexed_count,
        indexing_time_sec=elapsed,
        failed_papers=failed_papers,
    )
    return result.model_dump()
