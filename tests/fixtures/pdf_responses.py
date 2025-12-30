import httpx
import pytest


def _make_response(
    status_code: int, content: bytes, headers: dict | None = None
) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com/paper.pdf")
    return httpx.Response(
        status_code=status_code,
        content=content,
        headers=headers or {},
        request=request,
    )


@pytest.fixture
def mock_pdf_response() -> httpx.Response:
    return _make_response(
        200,
        b"%PDF-1.4\n%mock pdf content",
        headers={"content-type": "application/pdf"},
    )


@pytest.fixture
def mock_pdf_no_content_type() -> httpx.Response:
    return _make_response(
        200,
        b"%PDF-1.4\n%mock pdf content",
        headers={},
    )


@pytest.fixture
def mock_html_response() -> httpx.Response:
    return _make_response(
        200,
        b"<html><body>Access Denied</body></html>",
        headers={"content-type": "text/html"},
    )


@pytest.fixture
def mock_404_response() -> httpx.Response:
    return _make_response(
        404,
        b"Not Found",
        headers={"content-type": "text/plain"},
    )
