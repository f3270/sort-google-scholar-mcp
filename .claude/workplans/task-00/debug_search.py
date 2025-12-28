"""Quick debug search smoke test for ScholarSearcher.

Usage:
    uv run python .claude/workplans/task-00/debug_search.py
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sortgs_mcp.core import ScholarSearcher  # noqa: E402
from sortgs_mcp.models import SearchParams  # noqa: E402


async def main() -> None:
    searcher = ScholarSearcher(debug=True)
    params = SearchParams(keywords="transformers", num_results=10, debug=True)
    print("URL:", searcher.build_url(params))
    papers = await searcher.search(params)
    print(f"Papers: {len(papers)}")
    for paper in papers[:1]:
        print(f"- {paper.title} ({paper.citations} cites, {paper.cit_per_year} cit/yr)")

    if not papers:
        print("No papers returned. In debug mode we bundle a sample page; re-run if network fetch failed.")


if __name__ == "__main__":
    asyncio.run(main())
