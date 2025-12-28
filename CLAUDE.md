# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sortgs-mcp is a Python project that provides:
1. **sortgs**: Legacy CLI tool that scrapes and ranks Google Scholar publications by citation count
2. **sortgs-mcp**: Modern MCP (Model Context Protocol) server with RAG capabilities for integration with Claude

The project uses async/await patterns, persistent session management, and provides both a standalone CLI and an MCP server interface. When Google Scholar blocks requests with CAPTCHA, the tool falls back to Selenium WebDriver.

## Build and Development Commands

### Installation
```bash
# Recommended: sync deps and virtualenv with uv (creates .venv by default)
uv sync

# Fallback: editable install with pip (if uv unavailable)
pip install -e .
```

### Running Tests
```bash
uv run pytest
# or, without uv
pytest
```

### Running the Tools
```bash
# Legacy CLI
uv run sortgs "keyword"
uv run sortgs "machine learning" --nresults 100 --sortby "cit/year" --csvpath ./output
uv run sortgs "machine learning" --debug --nresults 10  # uses web archive

# MCP Server
uv run sortgs-mcp  # Starts the MCP server for Claude integration

# If installed via pip/uv globally, commands also work without `uv run`
# sortgs "keyword"
# sortgs-mcp
```

## Architecture

### Project Structure

```
sortgs-mcp/
├── src/
│   ├── sortgs/              # Legacy CLI (original implementation)
│   │   └── sortgs.py        # Monolithic CLI script
│   └── sortgs_mcp/          # MCP Server (refactored async architecture)
│       ├── config.py        # Settings and configuration (Pydantic Settings)
│       ├── models.py        # Data models (Paper, SearchParams, SearchSession)
│       ├── server.py        # MCP server entry point
│       └── core/
│           ├── scholar.py   # ScholarSearcher (async Google Scholar scraping)
│           ├── session.py   # SessionManager (JSON/CSV persistence)
│           └── parser.py    # HTML parsing utilities (BeautifulSoup)
```

### MCP Server Components (sortgs_mcp)

**src/sortgs_mcp/models.py** - Pydantic models for type safety:
- `SearchParams`: Search configuration (keywords, num_results, sort_by, year range)
- `Paper`: Publication metadata (title, author, citations, year, PDF link, etc.)
- `SearchSession`: Persistent session with search params and results

**src/sortgs_mcp/core/scholar.py** - `ScholarSearcher` class (async):
- `build_url()`: Constructs Google Scholar URLs with query parameters
- `fetch_page()`: Async HTTP requests with httpx
- `fetch_with_selenium()`: Selenium fallback for CAPTCHA (sync, run in thread)
- `search()`: Main async search orchestrator

**src/sortgs_mcp/core/session.py** - `SessionManager` class:
- `create_session()`: Generate UUID-based session directories
- `save_session()`: Persist session as JSON metadata + CSV results
- `load_session()`: Restore session from disk
- `list_sessions()`: Enumerate all saved sessions

**src/sortgs_mcp/core/parser.py** - HTML parsing utilities:
- `parse_google_scholar_page()`: Extract all papers from a results page
- Helper functions: `get_citations()`, `get_year()`, `get_author()`, `get_pdf_link()`

**src/sortgs_mcp/config.py** - Configuration management:
- `Settings` class using Pydantic Settings
- Environment variable support (.env file)
- Default paths for data storage and sessions

**Scraping Strategy**:
1. First attempts async fetch with httpx (fast, lightweight)
2. If robot check detected (CAPTCHA), falls back to Selenium WebDriver
3. Selenium driver runs in thread pool (`asyncio.to_thread()`)
4. Manual CAPTCHA solving: pauses execution and waits for user input

**Data Flow (MCP)**:
1. Build Google Scholar URL with query parameters (keyword, year range, language filter)
2. Fetch pages in batches of 10 results (Google Scholar pagination) via async iteration
3. Parse HTML with BeautifulSoup to extract: Title, Author, Citations, Year, Publisher, Venue, Content snippet, Source link, PDF link
4. Calculate citations per year: `Citations / (current_year - Year + 1)` if Year > 0
5. Create session and persist as JSON + CSV
6. Return session_id to MCP client

### Legacy CLI (sortgs)

**src/sortgs/sortgs.py** - Original monolithic implementation:
- Single module with all functionality embedded
- Sync-only implementation using requests library
- Direct pandas DataFrame manipulation and CSV export
- Maintained for backward compatibility

### Testing

Tests use pytest fixtures that run the CLI via `os.system()` in debug mode (uses web archive to avoid actual Google Scholar requests). Tests verify:
- Correct number of results returned
- Proper sorting by citations and cit/year
- Data accuracy against known archived results
- CSV file creation and structure
- PDF link extraction

### Key Constraints

- Google Scholar rate limiting: Tool adds random delays (0.5-3s) between requests to avoid blocks
- CAPTCHA handling: When detected, Selenium WebDriver pauses for manual solving
- Debug mode: Uses web.archive.org snapshot from 2021 for deterministic testing
- Filename length: CSV filenames are truncated to MAX_CSV_FNAME (255 chars)

### Dependencies

**Package Manager**: uv (recommended) - modern Python package manager with fast resolution
- Lock file: `uv.lock` ensures reproducible installs
- Fallback: pip with pyproject.toml

**Core Dependencies (defined in pyproject.toml)**:
- Web scraping: beautifulsoup4, requests, selenium, httpx
- Data handling: pandas, matplotlib
- MCP Server: mcp (Model Context Protocol SDK)
- AI integration: anthropic (Claude API client)
- Models & validation: pydantic, pydantic-settings
- RAG/Vector DB: chromadb, sentence-transformers, pymupdf, langchain-text-splitters
- Async utilities: aiofiles, tenacity

**System Requirements**:
- Python >=3.8
- ChromeDriver installed and available in PATH (for Selenium fallback)
- No API key needed for scraping (web scraping only)
- Optional: Anthropic API key for Claude integration in MCP server
