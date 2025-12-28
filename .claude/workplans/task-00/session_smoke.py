"""SessionManager quick smoke test (debug mode search + save/load).

Usage:
    uv run python .claude/workplans/task-00/session_smoke.py
"""

import asyncio
import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Minimal env for settings
os.environ.setdefault("ANTHROPIC_API_KEY", "debug-placeholder-key")

from sortgs_mcp.config import settings  # noqa: E402
from sortgs_mcp.core import ScholarSearcher, SessionManager  # noqa: E402
from sortgs_mcp.models import SearchParams, SearchSession  # noqa: E402


async def main() -> None:
    searcher = ScholarSearcher(debug=True)
    params = SearchParams(keywords="neural networks", num_results=10, debug=True)
    papers = await searcher.search(params)

    manager = SessionManager(settings.data_dir)
    session_id = manager.create_session(params)
    session = SearchSession(session_id=session_id, params=params, papers=papers)
    manager.save_session(session)
    loaded = manager.load_session(session_id)

    print(f"Created session: {session_id}")
    print(f"Papers saved: {len(papers)} | Papers loaded: {len(loaded.papers)}")
    sessions = manager.list_sessions()
    print("Sessions found:", [s.get("session_id") for s in sessions])


if __name__ == "__main__":
    asyncio.run(main())
