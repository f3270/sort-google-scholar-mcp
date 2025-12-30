from pathlib import Path

import pytest

from sortgs_mcp.pdf.parser import PDFParser
from tests.fixtures.generate_fixtures import NORMAL_PAGE_COUNT, build_page_lines


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _fixture_path(name: str) -> Path:
    return FIXTURES_DIR / name


def test_extract_text_normal_pdf():
    parser = PDFParser()
    pdf_path = _fixture_path("synthetic_normal.pdf")
    text = parser.extract_text(pdf_path)

    assert text is not None
    assert "Page 1/10" in text
    assert "Page 10/10" in text

    expected_length = sum(
        len("\n".join(build_page_lines(i + 1, NORMAL_PAGE_COUNT)))
        for i in range(NORMAL_PAGE_COUNT)
    )
    assert len(text) >= int(expected_length * 0.8)


def test_extract_text_corrupted_pdf(caplog):
    parser = PDFParser()
    pdf_path = _fixture_path("synthetic_corrupted.pdf")

    with caplog.at_level("WARNING"):
        text = parser.extract_text(pdf_path)

    assert text is None
    assert any(record.levelname == "WARNING" for record in caplog.records)


def test_extract_text_empty_pdf(caplog):
    parser = PDFParser()
    pdf_path = _fixture_path("synthetic_empty.pdf")

    with caplog.at_level("WARNING"):
        text = parser.extract_text(pdf_path)

    assert text is None
    assert any(record.levelname == "WARNING" for record in caplog.records)


def test_extract_text_multipage():
    parser = PDFParser()
    pdf_path = _fixture_path("synthetic_normal.pdf")
    text = parser.extract_text(pdf_path)

    assert text is not None
    assert text.count("Page ") >= NORMAL_PAGE_COUNT


def test_extract_text_nonexistent():
    parser = PDFParser()
    pdf_path = _fixture_path("does_not_exist.pdf")

    with pytest.raises(FileNotFoundError):
        parser.extract_text(pdf_path)
