from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_entry(entry_json_path: str | Path) -> dict[str, Any]:
    """Load one route history entry from JSON.

    The single-entry path mirrors the dashboard model where each route attempt
    is stored as one row.
    """
    path = Path(entry_json_path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Entry JSON must contain one object")

    return data


def load_history(history_json_path: str | Path) -> list[dict[str, Any]]:
    """Load a bulk dashboard history export from JSON."""
    path = Path(history_json_path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("History JSON must contain a list of entries")

    if not all(isinstance(item, dict) for item in data):
        raise ValueError("History JSON entries must be objects")

    return data


def get_response_text(entry: dict[str, Any]) -> str:
    """Return model response text from known history export fields."""
    value = entry.get("response_text") or entry.get("response") or entry.get("text") or ""
    return str(value)


def get_entry_metadata(entry: dict[str, Any]) -> dict[str, Any]:
    """Return history metadata that should be preserved in output rows."""
    return {
        "entry_id": entry.get("id", entry.get("entry_id")),
        "provider": entry.get("provider", "unknown"),
        "model": entry.get("model", "unknown"),
        "finish_status": entry.get("finish_status"),
        "max_output_tokens": entry.get("max_output_tokens"),
    }
