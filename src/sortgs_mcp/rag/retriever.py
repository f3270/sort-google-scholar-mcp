"""RAG retriever for question answering over indexed papers."""

from __future__ import annotations

import asyncio
import logging

from sortgs_mcp.models import QueryResult, QuerySource

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Answer questions by retrieving relevant chunks and calling an LLM."""

    def __init__(self, *, vectorstore, embedder, openai_client) -> None:
        self.vectorstore = vectorstore
        self.embedder = embedder
        self.openai_client = openai_client

    async def answer_question(
        self, question: str, session_id: str, top_k: int = 5
    ) -> QueryResult:
        """Run the RAG pipeline for a single question."""
        embedding = await asyncio.to_thread(self.embedder.embed_single, question)
        hits = self.vectorstore.query(embedding, session_id, k=top_k)

        if not hits:
            return QueryResult(
                question=question,
                answer="No relevant information found in indexed papers.",
                sources=[],
                session_id=session_id,
            )

        context = self._build_context(hits)
        answer = await self.openai_client.generate_answer(question, context)
        sources = self._build_sources(hits)

        return QueryResult(
            question=question,
            answer=answer,
            sources=sources,
            session_id=session_id,
        )

    @staticmethod
    def _build_context(hits: list[dict]) -> str:
        parts: list[str] = []
        for idx, hit in enumerate(hits, start=1):
            metadata = hit.get("metadata", {}) or {}
            title = metadata.get("paper_title", "Unknown title")
            authors = metadata.get("paper_authors", "Unknown authors")
            year = metadata.get("paper_year", "Unknown year")
            text = hit.get("text", "")
            parts.append(f"[{idx}] {title} ({authors}, {year}):\n{text}")
        return "\n\n".join(parts)

    @staticmethod
    def _build_sources(hits: list[dict]) -> list[QuerySource]:
        sources: list[QuerySource] = []
        for hit in hits:
            metadata = hit.get("metadata", {}) or {}
            distance = hit.get("distance", 1.0)
            similarity = 1.0 - float(distance)
            similarity = max(0.0, min(1.0, similarity))

            sources.append(
                QuerySource(
                    paper_title=metadata.get("paper_title", "Unknown title"),
                    chunk_text=hit.get("text", ""),
                    relevance_score=similarity,
                    metadata={
                        "authors": metadata.get("paper_authors"),
                        "year": metadata.get("paper_year"),
                        "citations": metadata.get("paper_citations"),
                        "source_url": metadata.get("source_url"),
                        "paper_rank": metadata.get("paper_rank"),
                        "chunk_index": metadata.get("chunk_index"),
                        "total_chunks": metadata.get("total_chunks"),
                        "session_id": metadata.get("session_id"),
                    },
                )
            )
        return sources
