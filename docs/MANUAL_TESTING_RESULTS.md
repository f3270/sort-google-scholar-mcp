# Manual Testing Results (MCP Inspector)

Status: Not executed in this environment. Fill "Obtained" and "Status" after running.

## Environment
- Date:
- Tester:
- MCP Inspector version:
- Node.js version:
- Project commit:

## Tools Checklist

### 1) generate_search_keywords
- Input:
  - query: "transformers attention mechanism"
  - num_variations: 3
- Expected:
  - JSON with `keywords` list (3 strings)
- Obtained:
- Status: pending
- Notes:

### 2) search_papers
- Input:
  - keywords: "transformers attention mechanism"
  - num_results: 10
  - sort_by: "Citations"
  - start_year: 2017
  - end_year: 2024
  - languages: ["en"]
  - debug: true
- Expected:
  - `session_id` (UUID string)
  - `papers_found` >= 1
  - `top_5_titles` list
  - `csv_path` pointing to `data/sessions/<id>/results.csv`
- Obtained:
- Status: pending
- Notes:

### 3) download_papers
- Input:
  - session_id: <from search_papers>
  - max_papers: 3
- Expected:
  - `downloaded` >= 0
  - `skipped` >= 0
  - `failed` >= 0
  - `pdf_paths` list
  - `download_metadata` list
- Obtained:
- Status: pending
- Notes:

### 4) index_papers
- Input:
  - session_id: <from search_papers>
  - chunk_size: 1000
  - chunk_overlap: 200
  - max_chunks: 10000
- Expected:
  - `papers_indexed` >= 1
  - `chunks_created` >= 1
  - `indexing_time_sec` > 0
  - `failed_papers` list (possibly empty)
- Obtained:
- Status: pending
- Notes:

### 5) query_papers
- Input:
  - question: "What is self-attention?"
  - session_id: <from search_papers>
  - top_k: 5
- Expected:
  - `answer` string
  - `sources` list with metadata fields
  - `session_id` matches input
- Obtained:
- Status: pending
- Notes:

### 6) list_sessions
- Input: none
- Expected:
  - `sessions` list with session metadata
- Obtained:
- Status: pending
- Notes:

## Claude Code Checklist

### 1) Tool availability
- Expected: 6 MCP tools visible
- Obtained:
- Status: pending
- Notes:

### 2) Search + download + index + query flow
- Expected: end-to-end flow works with same session_id
- Obtained:
- Status: pending
- Notes:
