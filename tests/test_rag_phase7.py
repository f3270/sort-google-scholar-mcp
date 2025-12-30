import asyncio

import httpx
import pytest
from openai import AuthenticationError, RateLimitError
from tenacity import wait_fixed

from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.llm.openai import OpenAIClient
from sortgs_mcp.models import QueryResult, SearchParams, SearchSession
from sortgs_mcp.rag.retriever import RAGRetriever
from sortgs_mcp.tools import query as query_tool


class FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = type("Msg", (), {"content": content})


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [FakeChoice(content)]
        self.usage = type(
            "Usage", (), {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )


class FakeEmbedder:
    def __init__(self) -> None:
        self.calls = []

    def embed_single(self, text: str) -> list[float]:
        self.calls.append(text)
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self, hits: list[dict]) -> None:
        self.hits = hits
        self.calls = []

    def query(self, embedding: list[float], session_id: str, k: int = 5) -> list[dict]:
        self.calls.append((session_id, k))
        return self.hits


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.calls = []

    async def generate_answer(self, question: str, context: str) -> str:
        self.calls.append((question, context))
        return "Answer with citation (Author et al., 2020)."


def create_session(tmp_path, *, indexed: bool) -> tuple[str, SessionManager]:
    params = SearchParams(
        keywords="test",
        num_results=10,
        sort_by="Citations",
    )
    session_id = "session-id"
    session = SearchSession(session_id=session_id, params=params, indexed=indexed)
    manager = SessionManager(tmp_path)
    manager.save_session(session)
    return session_id, manager


def make_error_response(status_code: int) -> httpx.Response:
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    return httpx.Response(status_code, request=request)


@pytest.mark.asyncio
async def test_generate_answer_success(monkeypatch):
    client = OpenAIClient(api_key="fake-key", model="gpt-4o-mini")

    async def fake_create(**kwargs):
        return FakeResponse("Synthetic answer.")

    monkeypatch.setattr(client.client.chat.completions, "create", fake_create)
    context = "a" * 6100 + "TAIL"
    answer = await client.generate_answer("What is X?", context)
    assert "Synthetic answer." == answer

    last_call = client.client.chat.completions.create
    assert callable(last_call)


@pytest.mark.asyncio
async def test_generate_answer_truncates_context(monkeypatch):
    client = OpenAIClient(api_key="fake-key", model="gpt-4o-mini")
    captured = {}

    async def fake_create(**kwargs):
        captured["prompt"] = kwargs["messages"][0]["content"]
        return FakeResponse("Answer.")

    monkeypatch.setattr(client.client.chat.completions, "create", fake_create)
    context = "a" * 6100 + "TAIL"
    await client.generate_answer("What is X?", context)
    prompt = captured["prompt"]
    assert "TAIL" not in prompt
    assert "What is X?" in prompt


@pytest.mark.asyncio
async def test_generate_answer_auth_error(monkeypatch):
    client = OpenAIClient(api_key="fake-key", model="gpt-4o-mini")

    async def fake_create(**kwargs):
        raise AuthenticationError(
            "bad key", response=make_error_response(401), body=None
        )

    monkeypatch.setattr(client.client.chat.completions, "create", fake_create)
    with pytest.raises(AuthenticationError):
        await client.generate_answer("Question", "Context")


@pytest.mark.asyncio
async def test_generate_answer_retry(monkeypatch):
    client = OpenAIClient(api_key="fake-key", model="gpt-4o-mini")
    calls = {"count": 0}

    async def fake_create(**kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RateLimitError(
                "rate limit", response=make_error_response(429), body=None
            )
        return FakeResponse("Recovered answer.")

    monkeypatch.setattr(client.client.chat.completions, "create", fake_create)
    original_wait = client.generate_answer.retry.wait
    client.generate_answer.retry.wait = wait_fixed(0)
    try:
        answer = await client.generate_answer("Question", "Context")
        assert answer == "Recovered answer."
        assert calls["count"] == 2
    finally:
        client.generate_answer.retry.wait = original_wait


@pytest.mark.asyncio
async def test_retriever_pipeline_mock():
    hits = [
        {
            "text": "Chunk one text.",
            "metadata": {
                "paper_title": "Paper One",
                "paper_authors": "A Author",
                "paper_year": 2020,
                "paper_citations": 5,
                "source_url": "https://example.com",
                "paper_rank": 1,
                "chunk_index": 0,
                "total_chunks": 2,
                "session_id": "session-id",
            },
            "distance": 0.2,
        },
        {
            "text": "Chunk two text.",
            "metadata": {
                "paper_title": "Paper Two",
                "paper_authors": "B Author",
                "paper_year": 2019,
                "paper_citations": 3,
                "source_url": "https://example.com/two",
                "paper_rank": 2,
                "chunk_index": 1,
                "total_chunks": 2,
                "session_id": "session-id",
            },
            "distance": 0.4,
        },
    ]
    retriever = RAGRetriever(
        vectorstore=FakeVectorStore(hits),
        embedder=FakeEmbedder(),
        openai_client=FakeOpenAIClient(),
    )
    result = await retriever.answer_question("What is it?", "session-id", top_k=2)
    assert result.answer
    assert len(result.sources) == 2
    assert result.sources[0].paper_title == "Paper One"
    assert result.sources[0].metadata["authors"] == "A Author"
    assert 0.0 <= result.sources[0].relevance_score <= 1.0


@pytest.mark.asyncio
async def test_retriever_no_results():
    retriever = RAGRetriever(
        vectorstore=FakeVectorStore([]),
        embedder=FakeEmbedder(),
        openai_client=FakeOpenAIClient(),
    )
    result = await retriever.answer_question("Question", "session-id", top_k=3)
    assert result.answer == "No relevant information found in indexed papers."
    assert result.sources == []


@pytest.mark.asyncio
async def test_sources_consistency_order():
    hits = [
        {
            "text": "First chunk.",
            "metadata": {"paper_title": "Paper A", "paper_authors": "A", "paper_year": 2020},
            "distance": 0.1,
        },
        {
            "text": "Second chunk.",
            "metadata": {"paper_title": "Paper B", "paper_authors": "B", "paper_year": 2019},
            "distance": 0.2,
        },
    ]
    retriever = RAGRetriever(
        vectorstore=FakeVectorStore(hits),
        embedder=FakeEmbedder(),
        openai_client=FakeOpenAIClient(),
    )
    result = await retriever.answer_question("Question", "session-id", top_k=2)
    assert result.sources[0].paper_title == "Paper A"
    assert result.sources[1].paper_title == "Paper B"


@pytest.mark.asyncio
async def test_query_papers_with_mocks(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = create_session(tmp_path, indexed=True)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    class FakeRetriever:
        def __init__(self, **kwargs) -> None:
            pass

        async def answer_question(self, question: str, session_id: str, top_k: int = 5):
            return QueryResult(
                question=question,
                answer="Mock answer.",
                sources=[],
                session_id=session_id,
            )

    monkeypatch.setattr(query_tool, "RAGRetriever", FakeRetriever)
    monkeypatch.setattr(query_tool, "_get_vectorstore", lambda: None)
    monkeypatch.setattr(query_tool, "_get_embedder", lambda: None)
    monkeypatch.setattr(query_tool, "_get_openai_client", lambda: None)

    result = await query_tool.query_papers("Question", session_id=session_id, top_k=2)
    assert result["answer"] == "Mock answer."
    assert result["session_id"] == session_id


@pytest.mark.asyncio
async def test_list_sessions(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    _, manager = create_session(tmp_path, indexed=False)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    response = await query_tool.list_sessions()
    assert response["sessions"]
    assert response["sessions"][0]["session_id"] == "session-id"


@pytest.mark.asyncio
async def test_query_session_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(query_tool, "session_manager", SessionManager(tmp_path))

    with pytest.raises(ValueError, match="Session missing not found"):
        await query_tool.query_papers("Question", session_id="missing")


@pytest.mark.asyncio
async def test_query_session_not_indexed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    session_id, manager = create_session(tmp_path, indexed=False)
    monkeypatch.setattr(query_tool, "session_manager", manager)

    with pytest.raises(RuntimeError, match="not indexed"):
        await query_tool.query_papers("Question", session_id=session_id)
