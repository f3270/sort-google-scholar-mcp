"""ChromaDB wrapper for session-scoped vector storage."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store wrapper over ChromaDB.

    Chunk IDs follow schema: {session_id}_chunk_{paper_rank:03d}_{chunk_index:03d}.
    """

    def __init__(
        self,
        persist_dir: Path,
        *,
        embedding_dim: int = 768,
        distance_metric: str = "cosine",
        model_name: str | None = None,
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.embedding_dim = embedding_dim
        self.distance_metric = distance_metric
        self.model_name = model_name
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

    def _collection_name(self, session_id: str) -> str:
        return f"session_{session_id}"

    def _collection_metadata(self) -> dict:
        metadata = {
            "hnsw:space": self.distance_metric,
            "embedding_dim": self.embedding_dim,
            "created_at": datetime.now().date().isoformat(),
        }
        if self.model_name:
            metadata["model"] = self.model_name
        return metadata

    def _generate_chunk_id(
        self, session_id: str, paper_rank: int, chunk_index: int
    ) -> str:
        return f"{session_id}_chunk_{paper_rank:03d}_{chunk_index:03d}"

    def get_or_create_collection(self, session_id: str):
        """Return the ChromaDB collection for a session."""
        return self.client.get_or_create_collection(
            name=self._collection_name(session_id),
            metadata=self._collection_metadata(),
        )

    def add_documents(
        self,
        session_id: str,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> int:
        """Add chunks + embeddings to the session collection with validation."""
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        if not chunks:
            return 0
        for embedding in embeddings:
            if len(embedding) != self.embedding_dim:
                raise ValueError(
                    f"Expected {self.embedding_dim} dims, got {len(embedding)}"
                )

        collection = self.get_or_create_collection(session_id)
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            if not isinstance(metadata, dict):
                raise ValueError("Chunk metadata must be a dict")
            paper_rank = metadata.get("paper_rank")
            chunk_index = metadata.get("chunk_index")
            if not isinstance(paper_rank, int) or not isinstance(chunk_index, int):
                raise ValueError("Chunk metadata missing paper_rank/chunk_index")
            ids.append(self._generate_chunk_id(session_id, paper_rank, chunk_index))
            documents.append(chunk.get("text", ""))
            metadatas.append(metadata)

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(chunks)

    def query(
        self, query_embedding: list[float], session_id: str, k: int = 5
    ) -> list[dict]:
        """Query the session collection for similar chunks."""
        if len(query_embedding) != self.embedding_dim:
            raise ValueError(
                f"Expected {self.embedding_dim} dims, got {len(query_embedding)}"
            )
        if k < 1:
            raise ValueError("k must be >= 1")

        collection = self.get_or_create_collection(session_id)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        hits: list[dict] = []
        ids = results.get("ids", [[]])[0] if results.get("ids") else []
        for idx, doc in enumerate(results.get("documents", [[]])[0]):
            hits.append(
                {
                    "id": ids[idx] if idx < len(ids) else None,
                    "text": doc,
                    "metadata": results.get("metadatas", [[]])[0][idx],
                    "distance": results.get("distances", [[]])[0][idx],
                }
            )
        return hits

    def delete_session(self, session_id: str) -> None:
        """Delete the collection for a given session."""
        name = self._collection_name(session_id)
        try:
            self.client.delete_collection(name=name)
        except Exception:
            logger.warning("Collection not found for deletion: %s", name)
