import pytest

from sortgs_mcp.rag import embeddings as embeddings_module


class FakeModel:
    def __init__(self, dim: int = 3) -> None:
        self.dim = dim
        self.calls: list[int] = []

    def encode(self, batch, show_progress_bar: bool = False):
        self.calls.append(len(batch))
        return [[float(len(text))] * self.dim for text in batch]

    def get_sentence_embedding_dimension(self) -> int:
        return self.dim


@pytest.fixture(autouse=True)
def reset_singleton():
    embeddings_module._SERVICE_INSTANCE = None
    embeddings_module._SERVICE_MODEL_NAME = None
    yield
    embeddings_module._SERVICE_INSTANCE = None
    embeddings_module._SERVICE_MODEL_NAME = None


def test_singleton_pattern(monkeypatch):
    model = FakeModel(dim=3)
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", lambda name: model)

    service1 = embeddings_module.get_embedding_service("fake-model")
    service2 = embeddings_module.get_embedding_service("fake-model")

    assert service1 is service2


def test_embed_single_dimensions(monkeypatch):
    model = FakeModel(dim=4)
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", lambda name: model)

    service = embeddings_module.get_embedding_service("fake-model")
    embedding = service.embed_single("hello")
    assert len(embedding) == 4


def test_embed_batch(monkeypatch):
    model = FakeModel(dim=5)
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", lambda name: model)

    service = embeddings_module.get_embedding_service("fake-model")
    embeddings = service.embed_texts(["a", "bb", "ccc"])
    assert len(embeddings) == 3


def test_sub_batching(monkeypatch):
    model = FakeModel(dim=2)
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", lambda name: model)

    service = embeddings_module.get_embedding_service("fake-model")
    texts = ["text"] * 2500
    embeddings = service.embed_texts(texts, batch_size=1000)

    assert len(embeddings) == 2500
    assert model.calls == [1000, 1000, 500]


def test_deterministic(monkeypatch):
    model = FakeModel(dim=3)
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", lambda name: model)

    service = embeddings_module.get_embedding_service("fake-model")
    embeddings = service.embed_texts(["same", "same"])
    assert embeddings[0] == embeddings[1]


def test_invalid_batch_size(monkeypatch):
    model = FakeModel(dim=3)
    monkeypatch.setattr(embeddings_module, "SentenceTransformer", lambda name: model)

    service = embeddings_module.get_embedding_service("fake-model")
    with pytest.raises(ValueError, match="batch_size must be >= 1"):
        service.embed_texts(["text"], batch_size=0)
