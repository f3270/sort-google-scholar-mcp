# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sortgs is a Python CLI tool that scrapes and ranks Google Scholar publications by citation count. It fetches search results from Google Scholar, parses the HTML using BeautifulSoup, and exports ranked results to CSV. When Google Scholar blocks requests with CAPTCHA, the tool falls back to Selenium WebDriver.

## Build and Development Commands

### Installation
```bash
# Recommended: sync deps and virtualenv with uv
uv sync

# Fallback: editable install with pip
pip install -e .
```

### Running Tests
```bash
uv run pytest
# or
pytest
```

### Running the CLI
```bash
uv run sortgs "keyword"
uv run sortgs "machine learning" --nresults 100 --sortby "cit/year" --csvpath ./output
uv run sortgs "machine learning" --debug --nresults 10  # uses web archive

# If installed via pip/uv globally, commands also work without `uv run`
# sortgs "keyword"
```

## Architecture

### Core Components

**src/sortgs/sortgs.py** - Single main module containing all functionality:
- `main()`: Entry point that orchestrates the scraping workflow
- `get_command_line_args()`: Argument parsing using argparse
- `get_content_with_selenium()`: Selenium fallback when requests are blocked
- Helper functions: `get_citations()`, `get_year()`, `get_author()`, `get_pdf_link()` for HTML parsing

**Scraping Strategy**:
1. First attempts to fetch results using `requests` library (fast, lightweight)
2. If robot check detected (CAPTCHA), falls back to Selenium WebDriver
3. Selenium driver is initialized once globally and reused across requests
4. Manual CAPTCHA solving: pauses execution and waits for user input

**Data Flow**:
1. Build Google Scholar URL with query parameters (keyword, year range, language filter)
2. Fetch pages in batches of 10 results (Google Scholar pagination)
3. Parse HTML with BeautifulSoup to extract: Title, Author, Citations, Year, Publisher, Venue, Content snippet, Source link, PDF link
4. Calculate citations per year: `Citations / (end_year + 1 - Year)`
5. Create pandas DataFrame and sort by specified column
6. Export to CSV with sanitized filename

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

Core: beautifulsoup4, pandas, requests, selenium, matplotlib
- Selenium requires ChromeDriver installed and available in PATH
- No API key needed (web scraping only)
