"""Core building blocks for Google Scholar MCP workflows."""

from sortgs_mcp.core.parser import (
    get_author,
    get_citations,
    get_pdf_link,
    get_year,
    parse_google_scholar_page,
)
from sortgs_mcp.core.scholar import ScholarSearcher
from sortgs_mcp.core.session import SessionManager

__all__ = [
    "ScholarSearcher",
    "SessionManager",
    "get_author",
    "get_citations",
    "get_pdf_link",
    "get_year",
    "parse_google_scholar_page",
]
