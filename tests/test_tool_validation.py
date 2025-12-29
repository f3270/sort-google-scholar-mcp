import asyncio

import pytest

from sortgs_mcp.tools.search import generate_search_keywords


def test_generate_search_keywords_empty_query():
    with pytest.raises(ValueError, match="query must not be empty"):
        asyncio.run(generate_search_keywords("   "))


def test_generate_search_keywords_invalid_variations_low():
    with pytest.raises(ValueError, match="num_variations must be an integer between 1 and 5"):
        asyncio.run(generate_search_keywords("machine learning", 0))


def test_generate_search_keywords_invalid_variations_high():
    with pytest.raises(ValueError, match="num_variations must be an integer between 1 and 5"):
        asyncio.run(generate_search_keywords("machine learning", 6))
