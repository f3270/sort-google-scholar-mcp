# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sortgs-mcp is a Python project that provides:
1. **sortgs**: Legacy CLI tool that scrapes and ranks Google Scholar publications by citation count
2. **sortgs-mcp**: Modern MCP (Model Context Protocol) server with RAG capabilities for integration with Claude

The project uses async/await patterns, persistent session management, PDF downloading with concurrency control, and provides both a standalone CLI and an MCP server interface. When Google Scholar blocks requests with CAPTCHA, the tool falls back to Selenium WebDriver.

## Development Philosophy

This project follows two core principles:

1. **KISS (Keep It Simple, Stupid)**: Favor simplicity over complexity. Avoid over-engineering, premature abstractions, and unnecessary features. Code should be straightforward, readable, and solve the current problem without anticipating hypothetical future requirements.

2. **TDD (Test-Driven Development)**: Write tests before implementation. All new features and bug fixes should:
   - Start with a failing test that defines the expected behavior
   - Implement the minimum code needed to make the test pass
   - Refactor while keeping tests green
   - Maintain high test coverage (aim for >80% coverage)
   - Use mocking to isolate units and avoid external dependencies

**TDD Workflow:**
```bash
# 1. Write a failing test
uv run pytest tests/test_new_feature.py -v  # Should fail

# 2. Implement the feature
# ... write minimal code ...

# 3. Run tests until they pass
uv run pytest tests/test_new_feature.py -v  # Should pass

# 4. Refactor if needed
# ... improve code while keeping tests green ...

# 5. Run full test suite
uv run pytest  # All tests should pass
```

## Build and Development Commands

### Installation
```bash
# Recommended: sync deps and virtualenv with uv (creates .venv by default)
uv sync

# Fallback: editable install with pip (if uv unavailable)
pip install -e .
```
Always use `uv run ...` for commands (including tests) so they run inside the
project environment and do not touch the system Python.

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
uv run pytest tests/test_pdf_downloader.py -v
uv run pytest tests/test_download_tool.py -v

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
- `test_pdf_downloader.py`: PDF downloader unit tests
  - Tests async PDF downloading with mocked HTTP responses
  - Tests validation (magic bytes, content-type), error handling (404, HTML responses)
  - Tests batch downloading with concurrency control
  - Uses mock httpx.AsyncClient to avoid network calls
- `test_download_tool.py`: MCP tool integration tests
  - Tests the download_papers MCP tool with mocked downloader
  - Tests session integration and metadata updates
  - Tests parameter validation (paper_indices, max_papers)

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
│       ├── models.py        # Data models (Paper, SearchParams, SearchSession, etc.)
│       ├── server.py        # MCP server entry point
│       ├── core/
│       │   ├── scholar.py   # ScholarSearcher (async Google Scholar scraping)
│       │   ├── session.py   # SessionManager (JSON/CSV persistence)
│       │   └── parser.py    # HTML parsing utilities (BeautifulSoup)
│       ├── pdf/
│       │   ├── __init__.py  # Exports PDFDownloader
│       │   └── downloader.py # Async PDF downloader with retry and validation
│       └── tools/
│           ├── search.py    # MCP tools for search and keyword generation
│           └── download.py  # MCP tool for downloading papers
```

### MCP Server Components (sortgs_mcp)

**src/sortgs_mcp/models.py** - Pydantic models for type safety:
- `SearchParams`: Search configuration (keywords, num_results, sort_by, year range)
- `Paper`: Publication metadata (title, author, citations, year, PDF link, etc.)
- `SearchSession`: Persistent session with search params and results
- `DownloadMetadata`: PDF download tracking (rank, title, file path, size, timestamp, status)
- `PDFDownloadResult`: Batch download results (counts, paths, failed papers, metadata)

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

**src/sortgs_mcp/pdf/downloader.py** - `PDFDownloader` class (async):
- `download_single()`: Downloads a single PDF with retry logic (3 attempts, exponential backoff)
- `download_batch()`: Downloads multiple PDFs with concurrency control (configurable limit)
- `_fetch_pdf()`: HTTP fetch with retry using tenacity (handles timeouts, HTTP errors)
- `_is_valid_pdf_header()`: Validates PDF magic bytes (%PDF) in file header
- `sanitize_filename()`: Creates safe filenames from paper titles
- Context manager support for proper httpx.AsyncClient lifecycle
- Skips existing valid PDFs unless force_redownload=True

**src/sortgs_mcp/tools/download.py** - MCP tool for downloading papers:
- `@mcp.tool() download_papers()`: Downloads PDFs for papers from a saved session
- Parameters: session_id (required), paper_indices (optional list), max_papers (default 10)
- Loads session, filters papers with PDF URLs, downloads in parallel
- Updates session metadata with download statistics
- Returns PDFDownloadResult with counts (downloaded/skipped/failed) and paths

**Scraping Strategy**:
1. First attempts async fetch with httpx (fast, lightweight)
2. If robot check detected (CAPTCHA), falls back to Selenium WebDriver
3. Selenium driver runs in thread pool (`asyncio.to_thread()`)
4. Manual CAPTCHA solving: pauses execution and waits for user input

**Data Flow (MCP Search)**:
1. Build Google Scholar URL with query parameters (keyword, year range, language filter)
2. Fetch pages in batches of 10 results (Google Scholar pagination) via async iteration
3. Parse HTML with BeautifulSoup to extract: Title, Author, Citations, Year, Publisher, Venue, Content snippet, Source link, PDF link
4. Calculate citations per year: `Citations / (current_year - Year + 1)` if Year > 0
5. Create session and persist as JSON + CSV
6. Return session_id to MCP client

**Data Flow (PDF Download)**:
1. Load session by session_id and filter papers with PDF URLs
2. Apply optional paper_indices filter and max_papers limit
3. For each paper, create sanitized filename (rank + title)
4. Create PDF directory: `data/sessions/{session_id}/pdfs/`
5. Download PDFs concurrently with semaphore-controlled parallelism
6. For each download:
   - Check if valid PDF already exists (skip if yes, unless force_redownload)
   - Fetch with retry (3 attempts, exponential backoff 2-10s)
   - Validate Content-Type header and PDF magic bytes (%PDF)
   - Write to disk with async file I/O
   - Track metadata (path, size, timestamp, status)
7. Update session with download counts and metadata
8. Return PDFDownloadResult with statistics and file paths

### Legacy CLI (sortgs)

**src/sortgs/sortgs.py** - Original monolithic implementation:
- Single module with all functionality embedded
- Sync-only implementation using requests library
- Direct pandas DataFrame manipulation and CSV export
- Maintained for backward compatibility

### Testing

Tests use pytest fixtures and mocking to avoid external dependencies:
- **Legacy CLI tests** (`test_sortgs.py`): Run CLI via `os.system()` in debug mode using web.archive.org
- **MCP Server tests**: Mock HTTP clients and file I/O to avoid network calls and filesystem side effects
- **Search tests** verify: Result count, sorting, CSV creation, data accuracy, PDF link extraction
- **PDF download tests** verify: Async downloading, retry logic, validation (magic bytes, content-type), error handling (404, HTML responses, timeouts), batch operations with concurrency control
- **Tool tests** verify: MCP tool integration, session management, parameter validation

### Key Constraints

- **Google Scholar rate limiting**: Tool adds random delays (0.5-3s) between requests to avoid blocks
- **CAPTCHA handling**: When detected, Selenium WebDriver pauses for manual solving
- **Debug mode**: Uses web.archive.org snapshot from 2021 for deterministic testing
- **Filename length**: CSV filenames are truncated to MAX_CSV_FNAME (255 chars)
- **PDF download concurrency**: Limited by `max_concurrent_downloads` setting (default: 5) to avoid overwhelming servers
- **PDF validation**: Both Content-Type header and magic bytes (%PDF) are checked; warning logged if Content-Type is missing/incorrect but magic bytes are valid
- **Retry logic**: Downloads retry up to 3 times with exponential backoff (2-10s) for timeouts and HTTP errors
- **Download timeout**: Each PDF download has a 30-second timeout (configurable)

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
