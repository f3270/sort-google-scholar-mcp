import asyncio

import pytest

from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.models import QueryResult, QuerySource, SearchParams, SearchSession
from sortgs_mcp.tools import query as query_tool


class FakeRetriever:
    async def answer_question(self, question, session_id, top_k=5):
        source = QuerySource(
            paper_title="Paper 1",
            chunk_text="Chunk",
            relevance_score=0.9,
            metadata={"paper_rank": 1},
        )
        return QueryResult(
            question=question,
            answer="Answer",
            sources=[source],
            session_id=session_id,
        )


def _create_session(session_id: str, indexed: bool) -> SearchSession:
    params = SearchParams(keywords="test", num_results=10, sort_by="Citations")
    return SearchSession(
        session_id=session_id,
        params=params,
        papers=[],
        papers_count=0,
        indexed=indexed,
    )


def test_query_papers_validation_errors():
    with pytest.raises(ValueError, match="question must not be empty"):
        asyncio.run(query_tool.query_papers("  ", session_id="s"))
    with pytest.raises(ValueError, match="top_k must be >= 1"):
        asyncio.run(query_tool.query_papers("q", session_id="s", top_k=0))
    with pytest.raises(ValueError, match="session_id is required"):
        asyncio.run(query_tool.query_papers("q"))


def test_query_papers_session_not_indexed(tmp_path, monkeypatch):
    manager = SessionManager(tmp_path)
    session = _create_session("session-1", indexed=False)
    manager.save_session(session)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    with pytest.raises(RuntimeError, match="not indexed"):
        asyncio.run(query_tool.query_papers("q", session_id="session-1"))


def test_query_papers_success(tmp_path, monkeypatch):
    manager = SessionManager(tmp_path)
    session = _create_session("session-2", indexed=True)
    manager.save_session(session)
    monkeypatch.setattr(query_tool, "session_manager", manager)
    monkeypatch.setattr(query_tool, "RAGRetriever", lambda **kwargs: FakeRetriever())
    monkeypatch.setattr(query_tool, "_get_openai_client", lambda: object())
    monkeypatch.setattr(query_tool, "_get_embedder", lambda: object())
    monkeypatch.setattr(query_tool, "_get_vectorstore", lambda: object())

    response = asyncio.run(
        query_tool.query_papers("What is RAG?", session_id="session-2", top_k=2)
    )
    assert response["answer"] == "Answer"
    assert response["sources"][0]["metadata"]["paper_rank"] == 1


def test_list_sessions(tmp_path, monkeypatch):
    manager = SessionManager(tmp_path)
    session = _create_session("session-3", indexed=True)
    manager.save_session(session)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    response = asyncio.run(query_tool.list_sessions())
    assert response["sessions"][0]["session_id"] == "session-3"
