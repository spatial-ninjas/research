"""Tests for the offline route-history evaluation script.

These tests cover script-level wrapper behavior only. They should not re-test
the shared route evaluator or network loader in detail.
"""

import json
from pathlib import Path

from scripts.evaluate_history import load_entry, load_history, get_response_text

import pytest


def test_evaluate_history_script_can_be_imported():
    import scripts.evaluate_history

    assert scripts.evaluate_history is not None


def test_load_entry_loads_single_entry_json(tmp_path):
    entry_path = tmp_path / "entry.json"
    entry = {
        "id": "entry-1",
        "provider": "openai",
        "model": "gpt-test",
    }
    entry_path.write_text(json.dumps(entry), encoding="utf-8")

    result = load_entry(entry_path)

    assert result == entry


def test_load_entry_rejects_non_object_json(tmp_path):
    entry_path = tmp_path / "entry.json"
    entry_path.write_text(json.dumps([{"id": "entry-1"}]), encoding="utf-8")

    with pytest.raises(ValueError, match="Entry JSON must contain one object"):
        load_entry(entry_path)


def test_load_history_loads_bulk_history_json(tmp_path):
    history_path = tmp_path / "history.json"
    history = [
        {"id": "entry-1", "provider": "openai"},
        {"id": "entry-2", "provider": "google"},
    ]
    history_path.write_text(json.dumps(history), encoding="utf-8")

    result = load_history(history_path)

    assert result == history


def test_load_history_rejects_non_list_json(tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps({"id": "entry-1"}), encoding="utf-8")

    with pytest.raises(ValueError, match="History JSON must contain a list"):
        load_history(history_path)


def test_load_history_rejects_non_object_entries(tmp_path):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps(["not an object"]), encoding="utf-8")

    with pytest.raises(ValueError, match="History JSON entries must be objects"):
        load_history(history_path)


def test_get_response_text_prefers_response_text():
    entry = {
        "response_text": "from response_text",
        "response": "from response",
        "text": "from text",
    }

    assert get_response_text(entry) == "from response_text"


def test_get_response_text_falls_back_to_response():
    entry = {
        "response": "from response",
        "text": "from text",
    }

    assert get_response_text(entry) == "from response"


def test_get_response_text_falls_back_to_text():
    entry = {"text": "from text"}

    assert get_response_text(entry) == "from text"


def test_get_response_text_returns_empty_string_when_missing():
    assert get_response_text({}) == ""


def test_get_response_text_converts_non_string_value_to_string():
    entry = {"response_text": 123}

    assert get_response_text(entry) == "123"
