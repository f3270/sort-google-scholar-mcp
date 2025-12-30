import math
import uuid

from sortgs_mcp.models import Paper
from sortgs_mcp.pdf.chunker import TextChunker


def make_paper() -> Paper:
    return Paper(
        rank=1,
        title="Test Paper",
        authors="A Author",
        citations=5,
        year=2021,
        publisher="Test Publisher",
        venue="Test Venue",
        content_snippet="Snippet",
        source_url="https://example.com/paper",
        pdf_url=None,
        cit_per_year=1,
    )


def test_chunk_short_text():
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    session_id = str(uuid.uuid4())
    text = "Short text " * 20

    chunks = chunker.chunk_paper(text, make_paper(), session_id)

    assert len(chunks) == 1
    metadata = chunks[0]["metadata"]
    assert metadata["chunk_index"] == 0
    assert metadata["total_chunks"] == 1
    assert len(chunks[0]["text"]) <= 1000


def test_chunk_long_text():
    chunk_size = 1000
    overlap = 200
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=overlap)
    session_id = str(uuid.uuid4())
    text = "a" * 5000

    chunks = chunker.chunk_paper(text, make_paper(), session_id)

    expected = math.ceil(max(len(text) - overlap, 0) / (chunk_size - overlap))
    assert len(chunks) == expected
    assert all(len(chunk["text"]) <= chunk_size for chunk in chunks)


def test_chunk_metadata_preservation():
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    session_id = str(uuid.uuid4())
    paper = make_paper()
    chunks = chunker.chunk_paper("Test content " * 50, paper, session_id)

    metadata = chunks[0]["metadata"]
    assert metadata["paper_title"] == paper.title
    assert metadata["paper_authors"] == paper.authors
    assert metadata["paper_year"] == paper.year
    assert metadata["paper_citations"] == paper.citations
    assert metadata["paper_rank"] == paper.rank
    assert metadata["source_url"] == paper.source_url


def test_chunk_indices():
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    session_id = str(uuid.uuid4())
    text = "abcde " * 500
    chunks = chunker.chunk_paper(text, make_paper(), session_id)

    indices = [chunk["metadata"]["chunk_index"] for chunk in chunks]
    total = chunks[0]["metadata"]["total_chunks"]
    assert indices == list(range(len(chunks)))
    assert total == len(chunks)
    assert indices[-1] == total - 1


def _overlap_length(left: str, right: str) -> int:
    max_len = min(len(left), len(right))
    for size in range(max_len, 0, -1):
        if left[-size:] == right[:size]:
            return size
    return 0


def test_chunk_overlap():
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    session_id = str(uuid.uuid4())
    text = ("abcdefghijklmnopqrstuvwxyz " * 100).strip()
    chunks = chunker.chunk_paper(text, make_paper(), session_id)

    overlaps = [
        _overlap_length(chunks[i]["text"], chunks[i + 1]["text"])
        for i in range(len(chunks) - 1)
    ]
    assert overlaps
    assert all(overlap >= 25 for overlap in overlaps)


def test_metadata_schema_validation():
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    session_id = str(uuid.uuid4())
    chunks = chunker.chunk_paper("Valid text " * 50, make_paper(), session_id)

    assert all(chunker.validate_chunk_metadata(chunk) for chunk in chunks)
