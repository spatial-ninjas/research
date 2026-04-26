"""Route-output parsing and graph-native evaluation utilities.

This module evaluates LLM-produced routes against an SSAL-derived graph. It
parses the expected route JSON contract, validates candidate paths using graph
edges, recomputes candidate length from the graph, and compares the result
against Dijkstra ground truth.

The evaluator does not trust model-declared route length or edge names as the
source of truth. Node IDs and graph edges determine validity.
"""

from __future__ import annotations

import json
import re
from typing import Any

from research.graph import Graph, dijkstra_shortest_path


_JSON_FENCE_RE = re.compile(
    r"`{3,}(?:json)?\s*(?P<json>\{.*?\})\s*`{3,}",
    re.DOTALL | re.IGNORECASE,
)

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def clean_json(text: str) -> str | None:
    """Recover a JSON-object string from a model response.

    The prompt asks for plain JSON only, but historical or imperfect model
    outputs may include Markdown fences or surrounding text. This function only
    extracts object-looking text; json.loads performs actual JSON validation
    later.
    """
    if not text or not isinstance(text, str):
        return None

    fenced = _JSON_FENCE_RE.search(text)
    if fenced:
        return fenced.group("json")

    plain = _JSON_OBJECT_RE.search(text)
    if plain:
        return plain.group(0)

    return None


def _extract_node_id(item: dict[str, Any]) -> str | None:
    """Extract a node ID from supported route entry keys."""
    node = item.get("node") or item.get("node_id") or item.get("id")
    if node is None:
        return None
    return str(node)


def _extract_raw_route(route_json: dict[str, Any]) -> list[Any]:
    """Extract the raw route list from supported route JSON fields."""
    raw_route = route_json.get("route")

    if raw_route is None:
        raw_route = route_json.get("path") or []

    if not isinstance(raw_route, list):
        return []

    return raw_route


def extract_path(route_json: dict[str, Any]) -> list[str]:
    """Extract candidate node IDs from the expected route JSON contract.

    The primary schema is route[*].node. Fallback handling exists only for
    older/manual outputs and should not replace the prompt contract. The
    edge_name field is intentionally ignored because graph edges determine
    route validity.
    """
    path: list[str] = []

    for item in _extract_raw_route(route_json):
        if isinstance(item, dict):
            node = _extract_node_id(item)
            if node is not None:
                path.append(node)
        elif isinstance(item, str):
            path.append(item)

    return path


def extract_route_entries(route_json: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract route entries while preserving edge_name for debugging/display.

    edge_name is not used for validation; only node IDs and graph edges
    determine route validity.
    """
    entries: list[dict[str, Any]] = []

    for item in _extract_raw_route(route_json):
        if not isinstance(item, dict):
            continue

        node = _extract_node_id(item)
        if node is None:
            continue

        entries.append(
            {
                "node": node,
                "edge_name": item.get("edge_name"),
            }
        )

    return entries


def extract_declared_length(route_json: dict[str, Any]) -> float | None:
    """Return the model-declared total_length if it can be parsed.

    The returned value is kept separate from graph-computed length so the
    evaluator can measure whether the model calculated its own route length
    correctly.
    """
    try:
        value = route_json.get("total_length")
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_candidate_path(
    graph: Graph,
    path: list[str],
    origin: str,
    destination: str,
) -> dict[str, Any]:
    """Validate whether a candidate path is legal in the directed graph.

    This checks route legality only. A valid path may still be non-shortest;
    shortest-path quality is measured separately against Dijkstra ground truth.
    """
    errors: list[str] = []

    if not path:
        errors.append("empty_path")
    else:
        if path[0] != origin:
            errors.append("wrong_origin")
        if path[-1] != destination:
            errors.append("wrong_destination")

    unknown_nodes = [node for node in path if not graph.has_node(node)]
    if unknown_nodes:
        errors.append("unknown_nodes")

    missing_edges: list[list[str]] = []

    if path and not unknown_nodes:
        for source, target in zip(path, path[1:]):
            if graph.get_edge(source, target) is None:
                # Lists are used instead of tuples so the result is directly
                # JSON-friendly for Streamlit display and exported evaluations.
                missing_edges.append([source, target])

    if missing_edges:
        errors.append("missing_edges")

    computed_length = None
    if not errors:
        computed_length = graph.path_length(path)

    return {
        "valid": not errors,
        "errors": errors,
        "unknown_nodes": unknown_nodes,
        "missing_edges": missing_edges,
        "computed_length": computed_length,
    }


def edge_set(path: list[str]) -> set[tuple[str, str]]:
    """Return directed edges from a node path."""
    return set(zip(path, path[1:]))


def overlap_ratio(candidate: set, reference: set) -> float:
    """Return the fraction of reference items covered by candidate items."""
    if not reference:
        return 0.0

    return len(candidate & reference) / len(reference)


def compare_routes(
    candidate_path: list[str],
    ground_truth_path: list[str],
    candidate_length: float | None,
    ground_truth_length: float | None,
) -> dict[str, Any]:
    """Compare a candidate route against one deterministic ground-truth route.

    This compares the candidate path against the single Dijkstra path currently
    used as ground truth. Equal-cost alternative shortest paths may still be
    valid even when exact_path_match is false.
    """
    candidate_nodes = set(candidate_path)
    ground_truth_nodes = set(ground_truth_path)

    candidate_edges = edge_set(candidate_path)
    ground_truth_edges = edge_set(ground_truth_path)

    exact_path_match = candidate_path == ground_truth_path

    node_overlap = (
        len(candidate_nodes & ground_truth_nodes) / len(ground_truth_nodes)
        if ground_truth_nodes
        else 0.0
    )

    edge_overlap = overlap_ratio(candidate_edges, ground_truth_edges)

    absolute_length_error = None
    relative_length_error = None

    if candidate_length is not None and ground_truth_length is not None:
        absolute_length_error = abs(candidate_length - ground_truth_length)

        if ground_truth_length > 0:
            relative_length_error = absolute_length_error / ground_truth_length

    return {
        "exact_path_match": exact_path_match,
        "node_overlap": node_overlap,
        "edge_overlap": edge_overlap,
        "absolute_length_error": absolute_length_error,
        "relative_length_error": relative_length_error,
    }


def compare_declared_length(
    declared_length: float | None,
    computed_length: float | None,
) -> dict[str, float | None]:
    """Compare the model-declared length against the graph-computed route length.

    This measures whether the model calculated the length of its own proposed
    route correctly. It is separate from candidate-vs-ground-truth comparison.
    """
    absolute_error = None
    relative_error = None

    if declared_length is not None and computed_length is not None:
        absolute_error = abs(declared_length - computed_length)

        if computed_length > 0:
            relative_error = absolute_error / computed_length

    return {
        "declared_length_absolute_error": absolute_error,
        "declared_length_relative_error": relative_error,
    }


def evaluate_route_response(
    response_text: str,
    graph: Graph,
    origin: str,
    destination: str,
) -> dict[str, Any]:
    """Evaluate one LLM route response against graph-native Dijkstra ground truth.

    The model-declared route length is kept separate from the graph-computed
    candidate length. Route validity and distance metrics are computed from the
    SSAL-derived graph.
    """
    cleaned = clean_json(response_text)

    if cleaned is None:
        return {
            "status": "skipped",
            "reason": "no_json_found",
            "valid_json": False,
            "valid_path": False,
        }

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {
            "status": "skipped",
            "reason": "invalid_json",
            "valid_json": False,
            "valid_path": False,
            "error": str(exc),
        }

    if not isinstance(parsed, dict):
        return {
            "status": "skipped",
            "reason": "json_not_object",
            "valid_json": True,
            "valid_path": False,
        }

    candidate_path = extract_path(parsed)
    candidate_declared_length = extract_declared_length(parsed)

    candidate_validation = validate_candidate_path(
        graph=graph,
        path=candidate_path,
        origin=origin,
        destination=destination,
    )

    # Ground truth is computed from the same graph representation shown to the
    # model, so candidate-vs-ground-truth metrics stay SSAL-native.
    ground_truth = dijkstra_shortest_path(
        graph=graph,
        origin=origin,
        destination=destination,
    )

    if not ground_truth.get("ok"):
        return {
            "status": "skipped",
            "reason": "ground_truth_failed",
            "valid_json": True,
            "valid_path": candidate_validation["valid"],
            "candidate_path": candidate_path,
            "candidate_declared_length": candidate_declared_length,
            "candidate_validation": candidate_validation,
            "ground_truth": ground_truth,
        }

    candidate_computed_length = candidate_validation.get("computed_length")

    route_metrics = compare_routes(
        candidate_path=candidate_path,
        ground_truth_path=ground_truth["path"],
        candidate_length=candidate_computed_length,
        ground_truth_length=ground_truth["total_length"],
    )

    declared_length_metrics = compare_declared_length(
        declared_length=candidate_declared_length,
        computed_length=candidate_computed_length,
    )

    return {
        "status": "evaluated",
        "valid_json": True,
        "valid_path": candidate_validation["valid"],
        "candidate_path": candidate_path,
        "candidate_declared_length": candidate_declared_length,
        "candidate_computed_length": candidate_computed_length,
        "candidate_validation": candidate_validation,
        "ground_truth_path": ground_truth["path"],
        "ground_truth_length": ground_truth["total_length"],
        **route_metrics,
        **declared_length_metrics,
    }
