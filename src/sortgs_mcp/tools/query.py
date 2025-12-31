"""MCP tools for RAG question answering."""

from __future__ import annotations

import logging

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.llm.openai import OpenAIClient
from sortgs_mcp.rag import VectorStore, get_embedding_service
from sortgs_mcp.rag.embeddings import EmbeddingService
from sortgs_mcp.rag.retriever import RAGRetriever
from sortgs_mcp.server import mcp

logger = logging.getLogger(__name__)
session_manager = SessionManager(settings.data_dir)

_openai_client: OpenAIClient | None = None
_vectorstore: VectorStore | None = None
_embedder: EmbeddingService | None = None


def _get_openai_client() -> OpenAIClient:
    """Return a cached OpenAI client for RAG queries."""
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            logger.error(
                "OPENAI_API_KEY missing for query_papers",
                extra={"openai_model": settings.openai_model_rag},
            )
            raise RuntimeError(
                "OPENAI_API_KEY not configured. "
                "Hint: Set OPENAI_API_KEY in .env to use RAG queries."
            )
        _openai_client = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model_rag,
        )
    return _openai_client


def _get_embedder() -> EmbeddingService:
    """Return a cached embedding service for RAG queries."""
    global _embedder
    if _embedder is None:
        _embedder = get_embedding_service(settings.embedding_model)
    return _embedder


def _get_vectorstore() -> VectorStore:
    """Return a cached vector store connection."""
    global _vectorstore
    if _vectorstore is None:
        embedder = _get_embedder()
        _vectorstore = VectorStore(
            settings.chroma_persist_dir,
            embedding_dim=embedder.embedding_dim,
            distance_metric="cosine",
            model_name=embedder.model_name,
        )
    return _vectorstore


@mcp.tool()
async def query_papers(
    question: str,
    session_id: str | None = None,
    top_k: int = 5,
) -> dict:
    """Answer a question using indexed papers in a session."""
    if not question.strip():
        logger.error(
            "Empty question in query_papers",
            extra={"session_id": session_id, "question_length": len(question)},
        )
        raise ValueError(
            "question must not be empty. " "Hint: Provide a short research question."
        )
    if top_k < 1:
        logger.error(
            "Invalid top_k in query_papers",
            extra={"session_id": session_id, "top_k": top_k},
        )
        raise ValueError("top_k must be >= 1. " "Hint: Use 3-5 for concise answers.")
    if session_id is None:
        logger.error(
            "Missing session_id in query_papers",
            extra={"top_k": top_k, "question_length": len(question)},
        )
        raise ValueError(
            "session_id is required for query_papers. "
            "Hint: Use list_sessions to pick a session."
        )

    logger.info(
        "query_papers called",
        extra={
            "session_id": session_id,
            "top_k": top_k,
            "question_length": len(question),
        },
    )

    try:
        session = session_manager.load_session(session_id)
    except FileNotFoundError as exc:
        logger.error(
            "Session not found for query_papers",
            extra={"session_id": session_id},
        )
        raise ValueError(
            f"Session '{session_id}' not found. "
            "Hint: Use list_sessions tool to see all sessions."
        ) from exc

    if not session.indexed:
        logger.error(
            "Session not indexed for query_papers",
            extra={"session_id": session_id},
        )
        raise RuntimeError(
            f"Session '{session_id}' not indexed. " "Hint: Run index_papers first."
        )

    retriever = RAGRetriever(
        vectorstore=_get_vectorstore(),
        embedder=_get_embedder(),
        openai_client=_get_openai_client(),
    )
    result = await retriever.answer_question(
        question=question,
        session_id=session_id,
        top_k=top_k,
    )
    logger.info(
        "query_papers answered",
        extra={
            "session_id": session_id,
            "top_k": top_k,
            "source_count": len(result.sources),
        },
    )
    return result.model_dump()


@mcp.tool()
async def list_sessions() -> dict:
    """List available search sessions with metadata."""
    sessions = session_manager.list_sessions()
    logger.info(
        "list_sessions called",
        extra={"session_count": len(sessions)},
    )
    return {"sessions": sessions}
