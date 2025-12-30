"""Session management utilities for search workflows."""

import json
import uuid
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

from sortgs_mcp.models import Paper, SearchParams, SearchSession


class SessionManager:
    """Manage search sessions with JSON and CSV persistence."""

    def __init__(self, data_dir: Path) -> None:
        self.sessions_dir = Path(data_dir) / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, params: SearchParams) -> str:
        """Create a new session directory and return its UUID."""
        session_id = str(uuid.uuid4())
        session_path = self.sessions_dir / session_id
        session_path.mkdir(parents=True, exist_ok=True)
        (session_path / "pdfs").mkdir(parents=True, exist_ok=True)
        return session_id

    def save_session(
        self, session: SearchSession, *, create_empty_csv: bool = True
    ) -> None:
        """Persist session metadata and results to disk."""
        session_path = self.sessions_dir / session.session_id
        session_path.mkdir(parents=True, exist_ok=True)
        (session_path / "pdfs").mkdir(parents=True, exist_ok=True)

        session.papers_count = len(session.papers)

        metadata_path = session_path / "metadata.json"
        metadata_path.write_text(
            session.model_dump_json(indent=2, exclude_none=True, by_alias=False)
        )

        csv_path = session_path / "results.csv"
        if pd is not None:
            if session.papers:
                df = pd.DataFrame([paper.model_dump() for paper in session.papers])
                df.to_csv(csv_path, index=False)
            elif create_empty_csv:
                columns = list(Paper.model_fields.keys())
                df = pd.DataFrame(columns=columns)
                df.to_csv(csv_path, index=False)
        elif create_empty_csv or session.papers:
            import csv

            fieldnames = list(Paper.model_fields.keys())
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for paper in session.papers:
                    writer.writerow(paper.model_dump())

    def load_session(self, session_id: str) -> SearchSession:
        """Load a session from disk."""
        metadata_path = self.sessions_dir / session_id / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Session metadata not found: {metadata_path}")
        json_data = metadata_path.read_text()
        return SearchSession.model_validate_json(json_data)

    def list_sessions(self) -> list[dict]:
        """List available sessions with basic metadata."""
        sessions: list[dict] = []
        for session_dir in self.sessions_dir.iterdir():
            metadata_path = session_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            try:
                session = SearchSession.model_validate_json(metadata_path.read_text())
                sessions.append(
                    {
                        "session_id": session.session_id,
                        "keywords": session.params.keywords,
                        "created_at": session.created_at.isoformat(),
                        "papers_count": session.papers_count,
                        "pdfs_downloaded": session.pdfs_downloaded,
                        "indexed": session.indexed,
                    }
                )
            except (json.JSONDecodeError, ValueError):
                continue
        return sessions
