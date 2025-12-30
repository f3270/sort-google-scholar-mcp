"""MCP tool implementations for Google Scholar search."""

import logging

import httpx

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.llm.openai import OpenAIClient
from sortgs_mcp.models import SearchParams, SearchSession
from sortgs_mcp.server import mcp

logger = logging.getLogger(__name__)
session_manager = SessionManager(settings.data_dir)


@mcp.tool()
async def search_papers(
    keywords: str,
    num_results: int = 100,
    sort_by: str = "Citations",
    start_year: int | None = None,
    end_year: int | None = None,
    languages: list[str] | None = None,
    debug: bool = False,
) -> dict:
    """Search Google Scholar for papers and persist the session.

    Returns a summary with session_id, number of papers found, top titles, and CSV path.
    """
    try:
        if not keywords.strip():
            raise ValueError(
                "keywords must not be empty. "
                "Hint: Provide a non-empty search string, e.g. 'machine learning'."
            )

        logger.info(
            "search_papers called",
            extra={"keywords": keywords, "num_results": num_results},
        )

        params = SearchParams(
            keywords=keywords,
            num_results=num_results,
            sort_by=sort_by,
            start_year=start_year,
            end_year=end_year,
            languages=languages,
            debug=debug,
        )

        session_id = session_manager.create_session(params)
        logger.info("Created session", extra={"session_id": session_id})

        from sortgs_mcp.core.scholar import ScholarSearcher

        async with ScholarSearcher(debug=debug) as searcher:
            papers = await searcher.search(params)

        session = SearchSession(
            session_id=session_id,
            params=params,
            papers=papers,
            papers_count=len(papers),
        )
        session_manager.save_session(session, create_empty_csv=True)
        logger.info(
            "Session saved",
            extra={"session_id": session_id, "papers_found": len(papers)},
        )

        top_5_titles = [paper.title for paper in papers[:5]]
        csv_path = str(settings.sessions_dir / session_id / "results.csv")
        return {
            "session_id": session_id,
            "papers_found": len(papers),
            "top_5_titles": top_5_titles,
            "csv_path": csv_path,
        }

    except ValueError as exc:
        logger.error(
            "Validation error in search_papers: %s",
            exc,
            extra={"keywords": keywords},
        )
        raise ValueError(f"Invalid parameters: {exc}") from exc
    except httpx.HTTPError as exc:
        logger.error(
            "HTTP error during search: %s",
            exc,
            extra={"keywords": keywords},
        )
        raise RuntimeError(
            "Failed to fetch results from Google Scholar. "
            "Hint: Use debug=True to rely on archived pages or retry later. "
            f"Details: {exc}"
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error in search_papers: %s",
            exc,
            extra={"keywords": keywords},
            exc_info=True,
        )
        raise RuntimeError(
            f"Search failed: {exc}. Hint: Retry with fewer results."
        ) from exc


@mcp.tool()
async def generate_search_keywords(query: str, num_variations: int = 3) -> dict:
    """Generate optimized Google Scholar search keywords using OpenAI."""
    if not query.strip():
        raise ValueError(
            "query must not be empty. "
            "Hint: Provide a short research topic or question."
        )

    if not isinstance(num_variations, int) or not (1 <= num_variations <= 5):
        raise ValueError(
            "num_variations must be an integer between 1 and 5. "
            "Hint: Try 3 for a balanced set."
        )

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not configured. "
            "Hint: Set it in .env to use keyword generation."
        )

    logger.info(
        "generate_search_keywords called",
        extra={"query": query[:100], "num_variations": num_variations},
    )

    client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model_keywords,
    )
    keywords = await client.generate_keywords(query, num_variations)

    logger.info(
        "Generated keywords successfully",
        extra={"keyword_count": len(keywords)},
    )
    return {"keywords": keywords}
