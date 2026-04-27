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
