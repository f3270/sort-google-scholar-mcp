from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from openai import AuthenticationError, RateLimitError

from sortgs_mcp.llm.openai import OpenAIClient, _is_retryable_exception


class FakeChat:
    def __init__(self, response):
        self.completions = SimpleNamespace(
            create=AsyncMock(return_value=response)
        )


class FakeClient:
    def __init__(self, response):
        self.chat = FakeChat(response)


def _make_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(
            prompt_tokens=10, completion_tokens=5, total_tokens=15
        ),
    )


def test_is_retryable_exception():
    rate_limit_exc = RateLimitError.__new__(RateLimitError)
    auth_exc = AuthenticationError.__new__(AuthenticationError)
    assert _is_retryable_exception(rate_limit_exc) is True
    assert _is_retryable_exception(auth_exc) is False


@pytest.mark.asyncio
async def test_generate_keywords_success(monkeypatch, caplog):
    response = _make_response('["kw1", "kw2", "kw3"]')
    monkeypatch.setattr(
        "sortgs_mcp.llm.openai.AsyncOpenAI",
        lambda api_key, timeout: FakeClient(response),
    )

    client = OpenAIClient(api_key="test")
    caplog.set_level("INFO")
    keywords = await client.generate_keywords("test query", 3)
    assert keywords == ["kw1", "kw2", "kw3"]
    assert "OpenAI keyword generation usage" in caplog.text


@pytest.mark.asyncio
async def test_generate_answer_success(monkeypatch):
    response = _make_response("Answer content")
    monkeypatch.setattr(
        "sortgs_mcp.llm.openai.AsyncOpenAI",
        lambda api_key, timeout: FakeClient(response),
    )

    client = OpenAIClient(api_key="test")
    result = await client.generate_answer("question", "context")
    assert result == "Answer content"


@pytest.mark.asyncio
async def test_generate_answer_trims_context(monkeypatch):
    response = _make_response("Answer content")
    fake_client = FakeClient(response)
    monkeypatch.setattr(
        "sortgs_mcp.llm.openai.AsyncOpenAI",
        lambda api_key, timeout: fake_client,
    )

    client = OpenAIClient(api_key="test")
    long_context = "x" * 7000
    await client.generate_answer("question", long_context)

    call = fake_client.chat.completions.create.call_args
    prompt = call.kwargs["messages"][0]["content"]
    assert long_context not in prompt
