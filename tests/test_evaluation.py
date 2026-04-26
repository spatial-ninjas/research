"""Tests for route-output parsing and evaluation utilities.

This module starts with JSON extraction tests for ``clean_json``. Later tests
should cover path extraction, candidate validation, route comparison metrics,
and top-level route-response evaluation.
"""

import pytest

from research.evaluation import clean_json


# ---------------------------------------------------------------------------
# JSON extraction
# ---------------------------------------------------------------------------


def test_clean_json_extracts_plain_json_object():
    """A valid JSON object should be returned unchanged."""
    text = '{"status": "success"}'

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_extracts_json_from_surrounding_text():
    """Historical or imperfect model outputs may include text around the JSON."""
    text = 'Here is the route: {"status": "success", "total_length": 3.0} Done.'

    assert clean_json(text) == '{"status": "success", "total_length": 3.0}'


def test_clean_json_extracts_json_from_fenced_json_block():
    """The evaluator should accept JSON fenced as a markdown json block."""
    text = """
```json
{"status": "success", "origin": "A", "destination": "D"}
```
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_json_from_generic_fenced_block():
    """Some models use a generic markdown code block instead of ```json."""
    text = """
```
{"status": "success", "origin": "A", "destination": "D"}
```
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_multiline_json_from_fenced_block():
    """Multiline JSON should be preserved so json.loads can parse it later."""
    text = """
```json
{
  "origin": "A",
  "destination": "D",
  "total_length": 3.0,
  "status": "success"
}
```
""".strip()

    expected = """{
  "origin": "A",
  "destination": "D",
  "total_length": 3.0,
  "status": "success"
}"""

    assert clean_json(text) == expected


def test_clean_json_extracts_json_from_four_backtick_fenced_json_block():
    """Some model outputs may use four-backtick json fences."""
    text = """
````json
{"status": "success", "origin": "A", "destination": "D"}
````
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_json_from_four_backtick_generic_fenced_block():
    """Generic fences may also use more than three backticks."""
    text = """
````
{"status": "success", "origin": "A", "destination": "D"}
````
""".strip()

    assert clean_json(text) == '{"status": "success", "origin": "A", "destination": "D"}'


def test_clean_json_extracts_json_when_closing_fence_is_shorter():
    """LLM markdown fences are sometimes inconsistent in length."""
    text = """
````json
{"status": "success"}
```
""".strip()

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_extracts_json_when_closing_fence_is_longer():
    """LLM markdown fences are sometimes inconsistent in length."""
    text = """
```json
{"status": "success"}
````
""".strip()

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_prefers_fenced_json_when_text_contains_other_braces():
    """A fenced block should avoid accidentally capturing unrelated braces."""
    text = """
Some explanation with {not json}.

```json
{"status": "success"}
```
""".strip()

    assert clean_json(text) == '{"status": "success"}'


def test_clean_json_returns_none_when_no_json_object_exists():
    """Responses without any JSON object should be skipped later."""
    assert clean_json("No route found.") is None


def test_clean_json_returns_none_for_empty_string():
    """Empty model output should not crash JSON extraction."""
    assert clean_json("") is None


def test_clean_json_returns_none_for_none_input():
    """Defensive behavior: non-string empty input should return None."""
    assert clean_json(None) is None  # type: ignore[arg-type]


def test_clean_json_returns_none_for_non_string_input():
    """Defensive behavior: non-string input should return None."""
    assert clean_json({"status": "success"}) is None  # type: ignore[arg-type]


def test_clean_json_extracts_invalid_json_text_for_later_json_decode_error():
    """clean_json only extracts object-looking text; json.loads validates later."""
    text = "{not valid json}"

    assert clean_json(text) == "{not valid json}"
