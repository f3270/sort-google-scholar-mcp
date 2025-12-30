"""MCP tools for RAG question answering."""

from __future__ import annotations

import logging

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.llm.openai import OpenAIClient
from sortgs_mcp.rag import VectorStore, get_embedding_service
from sortgs_mcp.rag.retriever import RAGRetriever
from sortgs_mcp.server import mcp

logger = logging.getLogger(__name__)
session_manager = SessionManager(settings.data_dir)

_openai_client: OpenAIClient | None = None
_vectorstore: VectorStore | None = None
_embedder = None


def _get_openai_client() -> OpenAIClient:
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not configured. "
                "Please set it in .env file to use RAG queries."
            )
        _openai_client = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model_rag,
        )
    return _openai_client


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = get_embedding_service(settings.embedding_model)
    return _embedder


def _get_vectorstore() -> VectorStore:
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
        raise ValueError("question must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if session_id is None:
        raise ValueError("session_id is required for query_papers")

    try:
        session = session_manager.load_session(session_id)
    except FileNotFoundError as exc:
        raise ValueError(f"Session {session_id} not found") from exc

    if not session.indexed:
        raise RuntimeError(
            f"Session {session_id} not indexed. Run index_papers first."
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
        extra={"session_id": session_id, "top_k": top_k},
    )
    return result.model_dump()


@mcp.tool()
async def list_sessions() -> dict:
    """List available search sessions with metadata."""
    sessions = session_manager.list_sessions()
    return {"sessions": sessions}
