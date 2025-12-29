"""Prompting and parsing helpers for keyword generation."""

from __future__ import annotations

import json
import re

KEYWORD_GENERATION_PROMPT = """You are an expert research assistant specializing in academic literature search.

Given a user's research query, generate {num_variations} optimized keyword variations for Google Scholar search.

User query: "{query}"

Requirements:
- Each variation should approach the topic from a different angle
- Use academic terminology and synonyms
- Include both broad and specific terms
- Optimize for Google Scholar's search algorithm
- Each variation should be 3-8 words

Return ONLY a JSON list of keyword strings, nothing else.

Example output format:
["keyword variation 1", "keyword variation 2", "keyword variation 3"]
"""


def build_keyword_prompt(query: str, num_variations: int) -> str:
    """Build prompt for keyword generation."""
    return KEYWORD_GENERATION_PROMPT.format(
        query=query,
        num_variations=num_variations,
    )


def parse_keyword_response(response: str) -> list[str]:
    """Parse OpenAI response content and extract a list of keywords."""
    # Try 1: direct JSON list
    try:
        keywords = json.loads(response)
        if isinstance(keywords, list) and all(isinstance(item, str) for item in keywords):
            return keywords
    except json.JSONDecodeError:
        pass

    # Try 2: JSON list inside markdown code block
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", response, re.DOTALL)
    if match:
        try:
            keywords = json.loads(match.group(1))
            if isinstance(keywords, list) and all(isinstance(item, str) for item in keywords):
                return keywords
        except json.JSONDecodeError:
            pass

    # Try 3: fallback - extract quoted strings
    keywords = re.findall(r'"([^"]+)"', response)
    if keywords:
        return keywords

    raise ValueError(f"Could not extract keywords from response: {response[:100]}")
