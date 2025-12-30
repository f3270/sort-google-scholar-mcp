"""Embedding service for RAG indexing."""

from __future__ import annotations

import logging
import threading

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_SERVICE_LOCK = threading.Lock()
_SERVICE_INSTANCE: "EmbeddingService | None" = None
_SERVICE_MODEL_NAME: str | None = None


class EmbeddingService:
    """Generate sentence-transformer embeddings with sub-batching support."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self.embedding_dim = self._model.get_sentence_embedding_dimension()
        logger.info(
            "Loaded embedding model",
            extra={"model": model_name, "embedding_dim": self.embedding_dim},
        )

    def embed_texts(
        self, texts: list[str], batch_size: int = 1000
    ) -> list[list[float]]:
        """Embed texts with automatic sub-batching."""
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        if not texts:
            return []

        all_embeddings: list[list[float]] = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for batch_index, start in enumerate(
            range(0, len(texts), batch_size), start=1
        ):
            batch = texts[start : start + batch_size]
            batch_embeddings = self._model.encode(batch, show_progress_bar=False)
            if hasattr(batch_embeddings, "tolist"):
                batch_embeddings = batch_embeddings.tolist()
            else:
                batch_embeddings = [list(embedding) for embedding in batch_embeddings]

            all_embeddings.extend(batch_embeddings)
            logger.info(
                "Embedded batch %s/%s",
                batch_index,
                total_batches,
                extra={"batch_size": len(batch), "total_texts": len(texts)},
            )

        return all_embeddings

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text input."""
        embeddings = self.embed_texts([text], batch_size=1)
        return embeddings[0]


def get_embedding_service(model_name: str) -> EmbeddingService:
    """Return a singleton EmbeddingService for the given model name."""
    global _SERVICE_INSTANCE, _SERVICE_MODEL_NAME
    with _SERVICE_LOCK:
        if _SERVICE_INSTANCE is None:
            _SERVICE_INSTANCE = EmbeddingService(model_name)
            _SERVICE_MODEL_NAME = model_name
        elif _SERVICE_MODEL_NAME != model_name:
            raise ValueError(
                "EmbeddingService already initialized with "
                f"{_SERVICE_MODEL_NAME}; requested {model_name}"
            )
    return _SERVICE_INSTANCE
