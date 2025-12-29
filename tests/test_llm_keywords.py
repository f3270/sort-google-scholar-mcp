import pytest

from sortgs_mcp.llm.keywords import parse_keyword_response


def test_parse_keyword_response_json():
    response = '["deep learning", "neural networks"]'
    assert parse_keyword_response(response) == ["deep learning", "neural networks"]


def test_parse_keyword_response_markdown_json():
    response = '```json\n["graph neural networks", "message passing"]\n```'
    assert parse_keyword_response(response) == ["graph neural networks", "message passing"]


def test_parse_keyword_response_quoted_fallback():
    response = 'Keywords: "transformers NLP", "attention mechanism"'
    assert parse_keyword_response(response) == ["transformers NLP", "attention mechanism"]


def test_parse_keyword_response_malformed():
    response = "not a list at all"
    with pytest.raises(ValueError, match="Could not extract keywords"):
        parse_keyword_response(response)


def test_parse_keyword_response_empty():
    response = "   "
    with pytest.raises(ValueError, match="Could not extract keywords"):
        parse_keyword_response(response)
