import pytest

from sortgs_mcp.rag import embeddings as embeddings_module


@pytest.mark.integration
def test_real_model_loading():
    embeddings_module._SERVICE_INSTANCE = None
    embeddings_module._SERVICE_MODEL_NAME = None
    service = embeddings_module.get_embedding_service("all-mpnet-base-v2")
    assert service.embedding_dim == 768


@pytest.mark.integration
def test_real_embedding_dims():
    embeddings_module._SERVICE_INSTANCE = None
    embeddings_module._SERVICE_MODEL_NAME = None
    service = embeddings_module.get_embedding_service("all-mpnet-base-v2")
    embeddings = service.embed_texts(["hello", "world"])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 768


@pytest.mark.integration
def test_real_sub_batching():
    embeddings_module._SERVICE_INSTANCE = None
    embeddings_module._SERVICE_MODEL_NAME = None
    service = embeddings_module.get_embedding_service("all-mpnet-base-v2")
    texts = ["text"] * 2500
    embeddings = service.embed_texts(texts, batch_size=1000)
    assert len(embeddings) == 2500
