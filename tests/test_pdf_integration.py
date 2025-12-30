import asyncio
import json
import os
import uuid
from pathlib import Path

import pytest

from sortgs_mcp.models import Paper
from sortgs_mcp.pdf import parse_and_chunk_pdf

FIXTURES_DIR = Path(__file__).parent / "fixtures"


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


class StubVectorStore:
    def add_documents(self, documents: list[dict]) -> int:
        for doc in documents:
            assert isinstance(doc.get("text"), str)
            assert isinstance(doc.get("metadata"), dict)
            json.dumps(doc["metadata"])
        return len(documents)


def test_chunk_metadata_schema_compatibility():
    pdf_path = FIXTURES_DIR / "synthetic_normal.pdf"
    session_id = str(uuid.uuid4())
    chunks = parse_and_chunk_pdf(pdf_path, make_paper(), session_id)

    assert chunks
    for chunk in chunks:
        json.dumps(chunk["metadata"])


def test_chunk_metadata_types():
    pdf_path = FIXTURES_DIR / "synthetic_normal.pdf"
    session_id = str(uuid.uuid4())
    chunks = parse_and_chunk_pdf(pdf_path, make_paper(), session_id)

    assert chunks
    sample = chunks[0]["metadata"]
    assert isinstance(sample["session_id"], str)
    assert isinstance(sample["paper_year"], int)
    assert isinstance(sample["paper_citations"], int)
    assert isinstance(sample["paper_rank"], int)
    assert isinstance(sample["chunk_index"], int)
    assert isinstance(sample["total_chunks"], int)


def test_chunk_metadata_ranges():
    pdf_path = FIXTURES_DIR / "synthetic_normal.pdf"
    session_id = str(uuid.uuid4())
    chunks = parse_and_chunk_pdf(pdf_path, make_paper(), session_id)

    assert chunks
    for chunk in chunks:
        metadata = chunk["metadata"]
        assert metadata["paper_year"] >= 1900
        assert metadata["paper_citations"] >= 0
        assert metadata["chunk_index"] < metadata["total_chunks"]


def test_chromadb_stub_integration():
    pdf_path = FIXTURES_DIR / "synthetic_normal.pdf"
    session_id = str(uuid.uuid4())
    chunks = parse_and_chunk_pdf(pdf_path, make_paper(), session_id)

    assert chunks
    store = StubVectorStore()
    assert store.add_documents(chunks) == len(chunks)


def test_async_compatibility():
    pdf_path = FIXTURES_DIR / "synthetic_normal.pdf"
    session_id = str(uuid.uuid4())

    async def run():
        return await asyncio.to_thread(
            parse_and_chunk_pdf, pdf_path, make_paper(), session_id
        )

    chunks = asyncio.run(run())
    assert chunks
    assert all("metadata" in chunk for chunk in chunks)


def test_error_propagation(tmp_path):
    if os.name == "nt":
        pytest.skip("Permission errors behave differently on Windows.")

    geteuid = getattr(os, "geteuid", None)
    if geteuid is not None and geteuid() == 0:
        pytest.skip("Cannot reliably trigger PermissionError when running as root.")

    pdf_path = tmp_path / "no_read.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%no access")
    pdf_path.chmod(0)

    try:
        with pytest.raises(PermissionError):
            parse_and_chunk_pdf(pdf_path, make_paper(), str(uuid.uuid4()))
    finally:
        pdf_path.chmod(0o644)
