import pytest

from sortgs_mcp.rag.vectorstore import VectorStore


def make_chunk(session_id: str, paper_rank: int, chunk_index: int, total_chunks: int):
    return {
        "text": f"chunk {paper_rank}-{chunk_index}",
        "metadata": {
            "session_id": session_id,
            "paper_title": f"Paper {paper_rank}",
            "paper_authors": "A Author",
            "paper_year": 2020,
            "paper_citations": 5,
            "paper_rank": paper_rank,
            "source_url": "https://example.com",
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
        },
    }


def test_init_chromadb(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    assert vectorstore.embedding_dim == 3


def test_collection_metadata(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3, distance_metric="cosine")
    collection = vectorstore.get_or_create_collection("session-1")
    assert collection.metadata["hnsw:space"] == "cosine"
    assert collection.metadata["embedding_dim"] == 3


def test_add_documents_valid_dims(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    chunks = [
        make_chunk("session-1", 1, 0, 2),
        make_chunk("session-1", 1, 1, 2),
    ]
    embeddings = [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]]
    count = vectorstore.add_documents("session-1", chunks, embeddings)
    collection = vectorstore.get_or_create_collection("session-1")
    assert count == 2
    assert collection.count() == 2


def test_add_documents_invalid_dims(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    chunks = [make_chunk("session-1", 1, 0, 1)]
    embeddings = [[0.1, 0.2]]
    with pytest.raises(ValueError, match="Expected 3 dims"):
        vectorstore.add_documents("session-1", chunks, embeddings)


def test_chunk_id_schema(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    chunk_id = vectorstore._generate_chunk_id("abc123", 1, 0)
    assert chunk_id == "abc123_chunk_001_000"


def test_query_session_specific(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    chunks = [make_chunk("session-1", 1, 0, 1)]
    embeddings = [[0.1, 0.2, 0.3]]
    vectorstore.add_documents("session-1", chunks, embeddings)

    results = vectorstore.query([0.1, 0.2, 0.3], "session-1", k=1)
    assert len(results) == 1
    assert results[0]["metadata"]["session_id"] == "session-1"


def test_query_dimension_mismatch(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    with pytest.raises(ValueError, match="Expected 3 dims"):
        vectorstore.query([0.1, 0.2], "session-1", k=1)


def test_delete_session(tmp_path):
    vectorstore = VectorStore(tmp_path, embedding_dim=3)
    vectorstore.get_or_create_collection("session-1")
    vectorstore.delete_session("session-1")
    names = [collection.name for collection in vectorstore.client.list_collections()]
    assert "session_session-1" not in names
