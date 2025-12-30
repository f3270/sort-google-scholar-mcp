# Sort Google Scholar by the Number of Citations

[MCP_PLAN.md](MCP_PLAN.md)

[![PyPI Version](https://img.shields.io/pypi/v/sortgs.svg)](https://pypi.org/project/sortgs/)

sortgs is a Python tool for ranking Google Scholar publications by the number of citations. It is useful for finding relevant papers in a specific field. The data acquired from Google Scholar includes Title, Citations, Links, Rank, and a new column with the number of citations per year. In the background, it first tries to fetch results using python requests. If it fails, it will use selenium to fetch the results.

This repo now also contains an MCP server that turns the CLI into a tool-driven research pipeline: search papers, download PDFs, parse + chunk PDFs for RAG, index into ChromaDB, and answer questions using OpenAI. The MCP plan and architecture are documented in `MCP_PLAN.md`.

## Project Intent (MCP)
The MCP server (`sortgs-mcp`) is intended to:
- Provide tool-based access to search, download, and inspect Google Scholar results.
- Build a local PDF corpus for a search session.
- Parse and chunk PDFs for RAG indexing (PyMuPDF + text splitters).
- Index chunks in a local vector store (ChromaDB).
- Answer questions using OpenAI over the indexed corpus.

High-level flow:
1. Generate keyword variations (OpenAI).
2. Search Google Scholar and create a session.
3. Download PDFs for the session.
4. Parse and chunk PDFs.
5. Index chunks in ChromaDB.
6. Query the corpus with RAG.

### MCP Server Setup (Quick)
```bash
# Install dev deps
uv sync

# Configure OpenAI (required for keyword generation and RAG)
cp .env.example .env
# edit .env to add OPENAI_API_KEY

# Run MCP server
uv run sortgs-mcp
```

### MCP Tools (Planned / In Progress)
- `generate_search_keywords`
- `search_papers`
- `download_papers`
- `index_papers`
- `query_papers`
- `list_sessions`

## Installation

**Option 1 (recommended for development): use `uv` for fast installs**
```bash
# from the repo root
uv sync

# run the CLI via uv
uv run sortgs "your keyword"
```

**Option 2: via pip (PyPI)**
```bash
pip install sortgs
```

## Usage

Once installed, you can run `sortgs` directly from the command line:

```bash
sortgs "your keyword"
```

Replace `"your keyword"` with any keyword you'd like to search for. A CSV file with the name `your_keyword.csv` will be created in your current directory.

### Examples

1. **Default Search**:
   ```bash
   sortgs "machine learning"
   ```
   This command searches for the top 100 results related to "machine learning" and saves them as a CSV file.

2. **Sort by Citations per Year**:
   ```bash
   sortgs "machine learning" --sortby "cit/year"
   ```
   Search for "machine learning" and sort by the number of citations per year.

3. **Specify Date Range**:
   ```bash
   sortgs "machine learning" --startyear 2005 --endyear 2015
   ```
   Search for papers from 2005 to 2015.

4. **Search for an Exact Keyword**:
   ```bash
   sortgs "'machine learning'"
   ```

5. **Save Results in a Specific Path**:
   ```bash
   sortgs 'neural networks' --csvpath './examples/'
   ```
   This will save the results under a subfolder called 'examples'.

6. **Multiple Keywords**:
   ```bash
   sortgs '"deep learning" OR "neural networks" OR "machine learning"' --sortby "cit/year"
   ```

7. **Language Filter**:
   ```bash
   sortgs "machine learning" --langfilter pt es fr de
   ```
   This will only include articles in Portuguese, Spanish, French, and German.

### Output Example

While running, `sortgs` will provide updates in the terminal:

```
❯ sortgs "'machine learning'"
Running with the following parameters:
Keyword: 'machine learning', Number of results: 100, Save database: True, Path: /Users/wittmann/sort-google-scholar, Sort by: Citations, Plot results: False, Start year: None, End year: 2023, Debug: False
Loading next 10 results
Loading next 20 results
...
```

   ```

   Replace `$PWD` with the absolute path to your results directory if you are not in the parent directory of `sortgs-results`.


## Contributing
We use `pytest` for our test suite. To run all tests:
```bash
# from repo root
uv run pytest

# or, after a pip editable install:
pytest
```
```bash
python -m pytest
```
Ensure all tests pass before submitting a PR; GitHub Actions will also execute the test suite on each push.

## About Robot Check
Google Scholar may block access after too many repetitive requests due to CAPTCHA checks. If this issue arrises, selenium will be used to attempt to fetch the results. You might be asked to solve a CAPTCHA manually. Ideally, you should use a VPN to avoid this issue. When using selenium, you might need to install chromedriver. You can download it from https://developer.chrome.com/docs/chromedriver/downloads and add it to your PATH.

## LICENSE
- MIT

## Updates
Main branch has been renamed from master. Update it locally by running:
```sh
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
```
## 💖 Support the Project

If you find this project helpful and would like to support its development, consider making a donation. Your support is greatly appreciated!

[Donate via Wise](https://wise.com/pay/me/fernandow21)
