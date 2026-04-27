"""Tests for the offline route-history evaluation script.

These tests cover script-level wrapper behavior only. They should not re-test
the shared route evaluator or network loader in detail.
"""

import json
from pathlib import Path

from scripts.evaluate_history import load_entry

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
