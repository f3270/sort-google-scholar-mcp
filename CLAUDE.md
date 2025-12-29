# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sortgs-mcp is a Python project that provides:
1. **sortgs**: Legacy CLI tool that scrapes and ranks Google Scholar publications by citation count
2. **sortgs-mcp**: Modern MCP (Model Context Protocol) server with RAG capabilities for integration with Claude

The project uses async/await patterns, persistent session management, PDF downloading with concurrency control, and provides both a standalone CLI and an MCP server interface. When Google Scholar blocks requests with CAPTCHA, the tool falls back to Selenium WebDriver.

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
# Run all tests (recommended)
uv run pytest

# Run tests with verbose output (shows each test individually)
uv run pytest -v

# Run tests with detailed output (shows print statements and full tracebacks)
uv run pytest -vv

# Run specific test file
uv run pytest tests/test_llm_keywords.py -v
uv run pytest tests/test_tool_validation.py -v
uv run pytest tests/test_sortgs.py -v

# Run specific test function
uv run pytest tests/test_llm_keywords.py::test_parse_keyword_response_json -v

# Run tests matching a pattern
uv run pytest -k "keyword" -v           # runs tests with "keyword" in name
uv run pytest -k "not validation" -v    # excludes validation tests

# Run tests and show warnings
uv run pytest -v --tb=short

# Run tests with coverage report (requires pytest-cov)
uv run pytest --cov=sortgs_mcp --cov-report=html

# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto

# Stop at first failure
uv run pytest -x

# Show local variables in tracebacks (useful for debugging)
uv run pytest -l

# Suppress warnings
uv run pytest --disable-warnings
```

**Test Categories:**
- `test_sortgs.py`: Legacy CLI tests using debug mode with web.archive.org (9 tests)
  - Tests result count, sorting, CSV creation, data accuracy, PDF links
  - Uses fixtures that run CLI commands with `--debug --endyear 2022`
  - Run time: ~37 seconds (due to CLI subprocess execution)
- `test_llm_keywords.py`: LLM keyword parsing tests (5 tests)
  - Tests JSON parsing, markdown-wrapped JSON, quoted strings, error handling
  - Fast unit tests (~0.01s)
- `test_tool_validation.py`: Tool input validation tests (3 tests)
  - Tests parameter validation for search keyword generation
  - Includes async function testing with `asyncio.run()`

**Writing New Tests:**
- Place tests in `tests/` directory with `test_*.py` naming convention
- Use pytest fixtures for setup/teardown (see `test_sortgs.py` for examples)
- For async code, use `asyncio.run()` or pytest-asyncio's `@pytest.mark.asyncio`
- Mock external API calls (OpenAI, Google Scholar) to avoid rate limits
- Use `tmp_path` fixture for temporary file operations
- Follow existing patterns for consistency

**Debugging Failed Tests:**
```bash
# Show full diff for assertion failures
uv run pytest --tb=long

# Drop into debugger on failure (requires ipdb or pdb)
uv run pytest --pdb

# Show stdout/stderr even for passing tests
uv run pytest -s

# Increase verbosity for more context
uv run pytest -vvv

# Run only last failed tests
uv run pytest --lf

# Run failed tests first, then others
uv run pytest --ff
```

**Common Test Issues:**
- Import errors: Ensure `uv sync` has been run to install the package
- Missing pytest: Run `uv add --dev pytest pytest-asyncio`
- Timeout errors: Increase timeout with `--timeout=300` (requires pytest-timeout)
- Async test failures: Check that async functions use `asyncio.run()` or `@pytest.mark.asyncio`

### Running the Tools
```bash
# Legacy CLI
uv run sortgs "keyword"
uv run sortgs "machine learning" --nresults 100 --sortby "cit/year" --csvpath ./output
uv run sortgs "machine learning" --debug --nresults 10  # uses web archive

# MCP Server
uv run sortgs-mcp  # Starts the MCP server for Claude Code integration

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
- AI integration: openai (OpenAI API client)
- Models & validation: pydantic, pydantic-settings
- RAG/Vector DB: chromadb, sentence-transformers, pymupdf, langchain-text-splitters
- Async utilities: aiofiles, tenacity

**Development Dependencies**:
- Testing: pytest, pytest-asyncio
- Optional: pytest-cov (coverage reports), pytest-xdist (parallel execution)

**System Requirements**:
- Python >=3.10 (updated from 3.8 for modern async features)
- ChromeDriver installed and available in PATH (for Selenium fallback)
- No API key needed for scraping (web scraping only)
- Optional: OpenAI API key for LLM integration in MCP server
