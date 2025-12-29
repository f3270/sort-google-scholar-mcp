# Repository Guidelines

## Project Structure & Modules
- Source lives in `src/sortgs/`; `sortgs.py` hosts the CLI, scraping, and CSV export logic.
- MCP server lives in `src/sortgs_mcp/` (tools, pdf, rag, core) with entrypoint in `src/sortgs_mcp/server.py`.
- Tests are in `tests/` and exercise the CLI against archived Scholar pages plus MCP units.
- Examples and helper scripts sit in `examples/` (e.g., `update_examples.py` updates demo CSVs).
- Packaging metadata: `pyproject.toml`; environment setups: `requirements.txt`, `conda_environment.yml`.

## Build, Test, and Development Commands
- Install in editable mode: `pip install -e .` (use Python ≥3.8).
- Run the CLI locally: `sortgs "machine learning" --nresults 20 --csvpath ./out`.
- Update demo CSVs: `python examples/update_examples.py`.
- Test suite: `pytest -q`. Note: CLI tests hit archived web pages (Wayback) and require network access.

## Coding Style & Naming
- Follow PEP 8 with 4-space indentation; prefer f-strings and pathlib for paths.
- Keep functions small; centralize logging via the module-level `logger` in `sortgs.py`.
- CLI options should mirror argparse names (e.g., `--sortby`, `--langfilter`); new columns should use lowercase with separators like `cit/year`.
- Avoid adding global state; pass explicit parameters into helpers where possible.

## Testing Guidelines
- Framework: `pytest`. Add fixtures when invoking the CLI to mirror `tests/test_sortgs.py`.
- Test names use `test_*` and should assert both structure (columns present) and representative values when stable.
- If scraping logic changes, refresh expectations in tests after confirming archived data still matches.

## Commit & Pull Request Guidelines
- Recent history uses short, imperative messages (`updates mcp workplan`, `fix mermaid workplan`); keep that style.
- PRs should describe behavior changes, flags added/removed, and any external calls required (e.g., Selenium/ChromeDriver expectations).
- Include reproduction steps and affected commands; attach screenshots only when UI output is relevant.

## Security & Configuration Notes
- Scraper can trigger Google Scholar bot checks; prefer `--debug` for deterministic, archived pages during development.
- Selenium requires ChromeDriver available on PATH; document any version pinning in your PR if you change driver usage.
