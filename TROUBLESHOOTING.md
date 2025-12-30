# Troubleshooting

## Google Scholar Robot Check

**Problem**: `search_papers` fails with "Robot check detected" or CAPTCHA errors.

**Symptoms**: Error message mentions CAPTCHA or robot verification.

**Solutions**:
1. Reduce `num_results` to < 50.
2. Use `debug=True` (uses archived pages).
3. Wait 15+ minutes before retrying.
4. Use a VPN if repeated failures occur.

## PDF Download Failures

**Problem**: `download_papers` reports failed downloads.

**Symptoms**: Some PDFs appear in the failed list.

**Solutions**:
1. Check if the PDF URL is valid (some papers do not have PDFs).
2. Retry with different papers or a smaller `max_papers`.
3. Check network connectivity.
4. Some publishers block automated downloads.

## OpenAI API Errors

**Problem**: Tools fail with OpenAI API errors.

**Symptoms**: Error mentions "API key" or "rate limit".

**Solutions**:
1. Verify `OPENAI_API_KEY` in `.env`.
2. Confirm the API key is valid in the OpenAI dashboard.
3. Check API usage limits.
4. Wait if rate limited.

## Embedding Model Already Initialized

**Problem**: `index_papers` fails with "EmbeddingService already initialized with X".

**Symptoms**: Error occurs when trying to use a different embedding model.

**Explanation**:
The embedding service uses a singleton pattern. Once initialized with a model,
it cannot be changed during the same MCP server session to prevent inconsistent
vector stores.

**Solutions**:
1. Restart the MCP server to change embedding models.
2. Use the same model across all indexing operations.
3. If you need multiple models, run separate MCP server instances.

## Understanding Log Format

**Log Structure**: MCP tools attach contextual metadata via structured logging.

**Example log entry**:
```
2025-12-30 10:30:45 - sortgs_mcp.tools.search - INFO - search_papers called
Extra context (attached to the log record): {'keywords': 'machine learning', 'num_results': 100}
```

**What to look for**:
- **Timestamp**: When the operation occurred.
- **Module**: Which tool/component logged the message.
- **Level**: INFO (normal), WARNING (attention), ERROR (failed).
- **Extra context**: Metadata like `session_id`, `paper_rank`, or `num_results`.
  The default log formatter does not print these fields, but they are attached
  to the log record for structured logging sinks.

**Troubleshooting with logs**:
1. Check `data/logs/sortgs_mcp.log` for detailed operations.
2. Look for ERROR level messages.
3. Use extra context to trace specific sessions or operations.
