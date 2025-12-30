import json
import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError

from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import SearchParams, SearchSession


def _create_session(session_id: str, params: SearchParams, papers=None):
    return SearchSession(
        session_id=session_id,
        params=params,
        papers=papers or [],
        papers_count=len(papers or []),
    )


def test_create_session_generates_uuid(tmp_path):
    manager = SessionManager(tmp_path)
    session_id = manager.create_session(SearchParams(keywords="test"))
    uuid.UUID(session_id)


def test_create_session_creates_directories(tmp_path):
    manager = SessionManager(tmp_path)
    session_id = manager.create_session(SearchParams(keywords="test"))
    session_dir = tmp_path / "sessions" / session_id
    assert session_dir.exists()
    assert (session_dir / "pdfs").exists()


def test_save_session_writes_json(tmp_path, sample_search_params):
    manager = SessionManager(tmp_path)
    session = _create_session("session-1", sample_search_params)
    manager.save_session(session)
    metadata_path = tmp_path / "sessions" / "session-1" / "metadata.json"
    assert metadata_path.exists()
    loaded = json.loads(metadata_path.read_text())
    assert loaded["session_id"] == "session-1"


def test_save_session_writes_csv(tmp_path, sample_search_params):
    manager = SessionManager(tmp_path)
    session = _create_session("session-2", sample_search_params)
    manager.save_session(session)
    csv_path = tmp_path / "sessions" / "session-2" / "results.csv"
    assert csv_path.exists()


def test_save_session_roundtrip(tmp_path, sample_search_params, sample_papers):
    manager = SessionManager(tmp_path)
    session = _create_session("session-3", sample_search_params, sample_papers)
    manager.save_session(session)
    loaded = manager.load_session("session-3")
    assert loaded.session_id == "session-3"
    assert loaded.papers_count == 2


def test_load_session_not_found(tmp_path):
    manager = SessionManager(tmp_path)
    with pytest.raises(FileNotFoundError):
        manager.load_session("missing")


def test_load_session_invalid_json(tmp_path):
    manager = SessionManager(tmp_path)
    session_dir = tmp_path / "sessions" / "broken"
    session_dir.mkdir(parents=True)
    metadata_path = session_dir / "metadata.json"
    metadata_path.write_text("{bad json")
    with pytest.raises((ValidationError, ValueError)):
        manager.load_session("broken")


def test_list_sessions_empty(tmp_path):
    manager = SessionManager(tmp_path)
    assert manager.list_sessions() == []


def test_list_sessions_multiple(tmp_path, sample_search_params):
    manager = SessionManager(tmp_path)
    session_a = _create_session("session-a", sample_search_params)
    session_b = _create_session("session-b", sample_search_params)
    manager.save_session(session_a)
    manager.save_session(session_b)

    sessions = manager.list_sessions()
    session_ids = {session["session_id"] for session in sessions}
    assert session_ids == {"session-a", "session-b"}


def test_list_sessions_skips_invalid_json(tmp_path):
    manager = SessionManager(tmp_path)
    session_dir = tmp_path / "sessions" / "broken"
    session_dir.mkdir(parents=True)
    (session_dir / "metadata.json").write_text("{bad json")
    assert manager.list_sessions() == []
