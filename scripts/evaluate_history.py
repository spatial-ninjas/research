"""Thin CLI helpers for offline route-history evaluation.

This script adapts dashboard history entries into calls to the shared
SSAL-native evaluator. Route parsing, graph validation, Dijkstra ground truth,
and metric computation should stay in research.evaluation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.evaluation import evaluate_route_response
from research.graph import Graph


def load_entry(entry_json_path: str | Path) -> dict[str, Any]:
    """Load one route-history entry from JSON.

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
    """Load a bulk dashboard history export from JSON.

    Bulk history is a convenience path. Each item should still be evaluated
    through the same single-entry helper used by the dashboard-style flow.
    """
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
    value = (
        entry.get("response_text")
        or entry.get("response")
        or entry.get("text")
        or ""
    )
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


def get_route_context(entry: dict[str, Any]) -> dict[str, str] | None:
    """Return origin/destination from explicit route metadata.

    Prompt parsing is intentionally avoided here so the script does not become
    another route parser. Older exports without route metadata should be skipped
    or handled by a separate compatibility helper later.
    """
    origin = entry.get("origin")
    destination = entry.get("destination")

    if origin is None or destination is None:
        origin = entry.get("route_origin")
        destination = entry.get("route_destination")

    if origin is None or destination is None:
        return None

    return {
        "origin": str(origin),
        "destination": str(destination),
    }


def evaluate_route_history_entry(
    entry: dict[str, Any],
    graph: Graph,
    ssal_hash: str,
) -> dict[str, Any]:
    """Evaluate one route-history row with the shared route evaluator.

    This function only adapts history-row metadata into the evaluator input.
    Route parsing, validation, Dijkstra, and metrics stay in
    research.evaluation.
    """
    metadata = get_entry_metadata(entry)

    route_context = get_route_context(entry)
    if route_context is None:
        return {
            **metadata,
            "ssal_hash": ssal_hash,
            "status": "skipped",
            "reason": "missing_route_context",
        }

    response_text = get_response_text(entry)

    evaluation = evaluate_route_response(
        response_text=response_text,
        graph=graph,
        origin=route_context["origin"],
        destination=route_context["destination"],
    )

    return {
        **metadata,
        "origin": route_context["origin"],
        "destination": route_context["destination"],
        "ssal_hash": ssal_hash,
        **evaluation,
    }
