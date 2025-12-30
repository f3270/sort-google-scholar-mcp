"""Async OpenAI client utilities for LLM keyword generation."""

from __future__ import annotations

import logging
from typing import Iterable

from openai import (
    APIConnectionError,
    APIError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from sortgs_mcp.llm.keywords import build_keyword_prompt, parse_keyword_response

logger = logging.getLogger(__name__)


def _is_retryable_exception(exc: Exception) -> bool:
    """Return True for retryable OpenAI errors (excluding auth failures)."""
    if isinstance(exc, AuthenticationError):
        return False
    return isinstance(exc, (RateLimitError, APIConnectionError, APIError))


class OpenAIClient:
    """Async client for OpenAI API with retry logic."""

    def __init__(
        self, api_key: str, model: str = "gpt-4o-mini", timeout: float = 30.0
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception(_is_retryable_exception),
        reraise=True,
    )
    async def generate_keywords(self, query: str, num_variations: int = 3) -> list[str]:
        """Generate keyword variations for Google Scholar search."""
        prompt = build_keyword_prompt(query, num_variations)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
            )
        except AuthenticationError as exc:
            logger.error("OpenAI authentication failed: %s", exc, exc_info=True)
            raise
        except (RateLimitError, APIConnectionError, APIError) as exc:
            logger.error("OpenAI API error: %s", exc, exc_info=True)
            raise

        content = response.choices[0].message.content or ""
        keywords = parse_keyword_response(content)
        self._log_usage(response.usage)
        return keywords

    async def generate_answer(self, question: str, context: str) -> str:
        """Generate an answer from context (stub for Phase 7)."""
        raise NotImplementedError(
            "RAG answer generation will be implemented in Phase 7"
        )

    def _log_usage(self, usage) -> None:
        if not usage:
            return
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        parts: Iterable[str] = (
            f"prompt_tokens={prompt_tokens}" if prompt_tokens is not None else None,
            (
                f"completion_tokens={completion_tokens}"
                if completion_tokens is not None
                else None
            ),
            f"total_tokens={total_tokens}" if total_tokens is not None else None,
        )
        message = ", ".join(part for part in parts if part)
        if message:
            logger.info("OpenAI keyword generation usage: %s", message)
