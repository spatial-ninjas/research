"""Thin wrappers for offline route-history evaluation.

This module adapts dashboard history entries into calls to the shared
SSAL-native evaluator. It should handle file loading, metadata preservation,
network-bundle loading, and output shaping only.

Route parsing, graph validation, Dijkstra ground truth, and metric computation
belong in research.evaluation.
"""

from __future__ import annotations

import json
import argparse
import os

from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from research.evaluation import evaluate_route_response
from research.graph import Graph
from research.network_loader import load_network_bundle_from_gpkg


DEFAULT_GPKG_PATH = "data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg"
DEFAULT_EDGES_LAYER = "slimmed_cropped_edges"
DEFAULT_NODES_LAYER = "slimmed_cropped_nodes"


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


def evaluate_entry_file(
    entry_json_path: str | Path,
    gpkg_path: str | Path,
    edges_layer: str,
    nodes_layer: str,
) -> dict[str, Any]:
    """Evaluate one route-history entry JSON file.

    This file-based wrapper loads the network bundle once, then delegates the
    actual route evaluation to evaluate_route_history_entry().
    """
    entry = load_entry(entry_json_path)

    bundle = load_network_bundle_from_gpkg(
        gpkg_path=gpkg_path,
        edges_layer=edges_layer,
        nodes_layer=nodes_layer,
    )

    return evaluate_route_history_entry(
        entry=entry,
        graph=bundle.graph,
        ssal_hash=bundle.ssal_hash,
    )


def evaluate_history_file(
    history_json_path: str | Path,
    gpkg_path: str | Path,
    edges_layer: str,
    nodes_layer: str,
) -> list[dict[str, Any]]:
    """Evaluate a bulk dashboard history export.

    Bulk mode is only a convenience wrapper around the single-entry evaluator.
    The network bundle is loaded once and reused for every entry.
    """
    history = load_history(history_json_path)

    bundle = load_network_bundle_from_gpkg(
        gpkg_path=gpkg_path,
        edges_layer=edges_layer,
        nodes_layer=nodes_layer,
    )

    return [
        evaluate_route_history_entry(
            entry=entry,
            graph=bundle.graph,
            ssal_hash=bundle.ssal_hash,
        )
        for entry in history
    ]


def _average(values: list[float]) -> float | None:
    """Return the mean value, or None when no values are available."""
    if not values:
        return None

    return sum(values) / len(values)


def _model_key(row: dict[str, Any]) -> str:
    """Return a stable provider/model grouping key for summaries."""
    provider = row.get("provider") or "unknown"
    model = row.get("model") or "unknown"
    return f"{provider}/{model}"


def _route_key(row: dict[str, Any]) -> str:
    """Return a stable origin/destination grouping key for summaries."""
    origin = row.get("origin") or "unknown"
    destination = row.get("destination") or "unknown"
    return f"{origin}->{destination}"


def _group_results_by(
    results: list[dict[str, Any]],
    key_fn: Callable[[dict[str, Any]], str],
) -> dict[str, list[dict[str, Any]]]:
    """Group result rows by a derived summary key."""
    groups: dict[str, list[dict[str, Any]]] = {}

    for row in results:
        groups.setdefault(key_fn(row), []).append(row)

    return groups


def _summarize_result_group(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize one group of evaluation rows."""
    evaluated = [row for row in results if row.get("status") == "evaluated"]
    skipped = [row for row in results if row.get("status") == "skipped"]

    skip_reasons = Counter(row.get("reason") or "unknown" for row in skipped)

    valid_path_values = [
        1.0 if row.get("valid_path") else 0.0
        for row in evaluated
        if "valid_path" in row
    ]

    relative_errors = [
        row["relative_length_error"]
        for row in evaluated
        if row.get("relative_length_error") is not None
    ]

    declared_errors = [
        row["declared_length_relative_error"]
        for row in evaluated
        if row.get("declared_length_relative_error") is not None
    ]

    return {
        "total_entries": len(results),
        "evaluated_entries": len(evaluated),
        "skipped_entries": len(skipped),
        "skip_reasons": dict(skip_reasons),
        "valid_path_rate": _average(valid_path_values),
        "average_relative_length_error": _average(relative_errors),
        "average_declared_length_relative_error": _average(declared_errors),
    }


def _summarize_groups(
    groups: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """Summarize grouped evaluation rows with deterministic key ordering."""
    return {
        key: _summarize_result_group(rows)
        for key, rows in sorted(groups.items())
    }


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Return aggregate and grouped summaries for bulk evaluation rows."""
    summary = _summarize_result_group(results)

    summary["per_model"] = _summarize_groups(
        _group_results_by(results, _model_key)
    )
    summary["per_route"] = _summarize_groups(
        _group_results_by(results, _route_key)
    )

    return summary


def write_results_json(
    output_path: str | Path,
    *,
    result: dict[str, Any] | None = None,
    results: list[dict[str, Any]] | None = None,
    summary: dict[str, Any] | None = None,
) -> None:
    """Write one-entry or bulk evaluation output as JSON."""
    has_single_payload = result is not None
    has_bulk_payload = results is not None or summary is not None

    if has_single_payload == has_bulk_payload:
        raise ValueError("write_results_json requires exactly one output mode")

    if has_bulk_payload and (results is None or summary is None):
        raise ValueError("bulk output requires results and summary")

    if has_single_payload:
        payload = {"result": result}
    else:
        payload = {
            "summary": summary,
            "results": results,
        }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for one-entry or bulk history evaluation."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate route-history entries with the shared "
            "SSAL-native evaluator."
        )
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--entry-json",
        help="Path to a JSON file containing one route history entry.",
    )
    input_group.add_argument(
        "--history-json",
        help="Path to a JSON file containing a bulk route history export.",
    )

    parser.add_argument(
        "--gpkg-path",
        default=os.getenv("GPKG_PATH", DEFAULT_GPKG_PATH),
        help=(
            "Path to GeoPackage file "
            f"(default: env GPKG_PATH or {DEFAULT_GPKG_PATH})."
        ),
    )
    parser.add_argument(
        "--edges-layer",
        default=os.getenv("EDGES_LAYER", DEFAULT_EDGES_LAYER),
        help=(
            "GeoPackage edge layer "
            f"(default: env EDGES_LAYER or {DEFAULT_EDGES_LAYER})."
        ),
    )
    parser.add_argument(
        "--nodes-layer",
        default=os.getenv("NODES_LAYER", DEFAULT_NODES_LAYER),
        help=(
            "GeoPackage node layer "
            f"(default: env NODES_LAYER or {DEFAULT_NODES_LAYER})."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path.",
    )

    return parser.parse_args(argv)
