#!/usr/bin/env python3
"""Generate synthetic PDF fixtures for testing."""

from __future__ import annotations

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent

NORMAL_PAGE_COUNT = 10
NORMAL_SECTIONS = ["Introduction", "Methods", "Results", "Discussion", "Conclusion"]
LOREM_SENTENCE = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)
NORMAL_REPEAT_LINES = 6

SHORT_TEXT_LINES = [
    "Short fixture page",
    "Section: Summary",
    LOREM_SENTENCE,
]


def build_page_lines(page_num: int, total_pages: int) -> list[str]:
    """Build consistent text lines for a given page."""
    section = NORMAL_SECTIONS[(page_num - 1) % len(NORMAL_SECTIONS)]
    lines = [
        f"Page {page_num}/{total_pages}",
        f"Section: {section}",
        "Keywords: Introduction, Methods, Results, Discussion",
    ]
    lines.extend([LOREM_SENTENCE] * NORMAL_REPEAT_LINES)
    return lines


def build_short_lines() -> list[str]:
    """Build short PDF content lines."""
    return list(SHORT_TEXT_LINES)


def _generate_with_reportlab(pdf_path: Path, pages: list[list[str]]) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    canvas_obj = canvas.Canvas(str(pdf_path), pagesize=letter)
    for lines in pages:
        text = canvas_obj.beginText(50, 750)
        for line in lines:
            text.textLine(line)
        canvas_obj.drawText(text)
        canvas_obj.showPage()
    canvas_obj.save()


def _generate_with_pymupdf(pdf_path: Path, pages: list[list[str]]) -> None:
    import fitz

    doc = fitz.open()
    for lines in pages:
        page = doc.new_page()
        rect = fitz.Rect(50, 50, 550, 750)
        page.insert_textbox(rect, "\n".join(lines), fontsize=12)
    doc.save(pdf_path)
    doc.close()


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_content_stream(lines: list[str]) -> str:
    content_lines = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
    for idx, line in enumerate(lines):
        if idx > 0:
            content_lines.append("T*")
        content_lines.append(f"({_escape_pdf_text(line)}) Tj")
    content_lines.append("ET")
    return "\n".join(content_lines)


def _generate_with_minimal_pdf(pdf_path: Path, pages: list[list[str]]) -> None:
    page_count = len(pages)
    font_obj_num = 3 + page_count
    content_start = font_obj_num + 1
    max_obj = content_start + page_count - 1

    objects: dict[int, str] = {}
    objects[1] = "<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{3 + i} 0 R" for i in range(page_count))
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>"

    for i in range(page_count):
        page_num = 3 + i
        content_num = content_start + i
        objects[page_num] = (
            "<< /Type /Page /Parent 2 0 R "
            f"/Resources << /Font << /F1 {font_obj_num} 0 R >> >> "
            "/MediaBox [0 0 612 792] "
            f"/Contents {content_num} 0 R >>"
        )

    objects[font_obj_num] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    for i, lines in enumerate(pages):
        stream = _build_content_stream(lines)
        objects[content_start + i] = (
            f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"
        )

    result = bytearray()
    result.extend(b"%PDF-1.4\n")
    offsets = [0]

    for obj_num in range(1, max_obj + 1):
        offsets.append(len(result))
        obj = objects[obj_num]
        result.extend(f"{obj_num} 0 obj\n{obj}\nendobj\n".encode("ascii"))

    xref_pos = len(result)
    result.extend(f"xref\n0 {max_obj + 1}\n".encode("ascii"))
    result.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    result.extend(
        f"trailer\n<< /Size {max_obj + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )

    pdf_path.write_bytes(result)


def generate_normal_pdf() -> Path:
    """Generate multi-page PDF with known content."""
    pdf_path = FIXTURES_DIR / "synthetic_normal.pdf"
    pages = [
        build_page_lines(i + 1, NORMAL_PAGE_COUNT) for i in range(NORMAL_PAGE_COUNT)
    ]
    try:
        _generate_with_reportlab(pdf_path, pages)
    except ModuleNotFoundError:
        try:
            _generate_with_pymupdf(pdf_path, pages)
        except ModuleNotFoundError:
            _generate_with_minimal_pdf(pdf_path, pages)
    return pdf_path


def generate_short_pdf() -> Path:
    """Generate short, single-page PDF."""
    pdf_path = FIXTURES_DIR / "synthetic_short.pdf"
    pages = [build_short_lines()]
    try:
        _generate_with_reportlab(pdf_path, pages)
    except ModuleNotFoundError:
        try:
            _generate_with_pymupdf(pdf_path, pages)
        except ModuleNotFoundError:
            _generate_with_minimal_pdf(pdf_path, pages)
    return pdf_path


def generate_empty_pdf() -> Path:
    """Generate PDF with no text."""
    pdf_path = FIXTURES_DIR / "synthetic_empty.pdf"
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        canvas_obj = canvas.Canvas(str(pdf_path), pagesize=letter)
        canvas_obj.showPage()
        canvas_obj.save()
    except ModuleNotFoundError:
        try:
            import fitz

            doc = fitz.open()
            doc.new_page()
            doc.save(pdf_path)
            doc.close()
        except ModuleNotFoundError:
            _generate_with_minimal_pdf(pdf_path, [[]])
    return pdf_path


def generate_corrupted_pdf(source_pdf: Path) -> Path:
    """Generate a corrupted PDF by truncating the source file."""
    pdf_path = FIXTURES_DIR / "synthetic_corrupted.pdf"
    content = source_pdf.read_bytes()
    cutoff = max(1, len(content) // 2)
    pdf_path.write_bytes(content[:cutoff])
    return pdf_path


def generate_all() -> None:
    """Generate all synthetic fixtures."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    normal = generate_normal_pdf()
    generate_short_pdf()
    generate_empty_pdf()
    generate_corrupted_pdf(normal)


if __name__ == "__main__":
    generate_all()
