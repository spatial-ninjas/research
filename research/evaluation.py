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
    """Extract a JSON object from a model response.

    The prompt asks for plain JSON only, but this function also accepts fenced
    JSON to make offline evaluation robust against imperfect model outputs.
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


def extract_path(route_json: dict[str, Any]) -> list[str]:
    """Extract candidate node IDs from the expected route JSON contract.

    The primary schema is route[*].node. Fallback handling exists only for
    older/manual outputs and should not replace the prompt contract.
    """
    raw_route = route_json.get("route")

    if raw_route is None:
        raw_route = route_json.get("path") or []

    path: list[str] = []

    if not isinstance(raw_route, list):
        return path

    for item in raw_route:
        if isinstance(item, dict):
            node = item.get("node") or item.get("node_id") or item.get("id")
            if node is not None:
                path.append(str(node))
        elif isinstance(item, str):
            path.append(item)

    return path


def extract_declared_length(route_json: dict[str, Any]) -> float | None:
    """Return the model-declared total_length if it can be parsed."""
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
    """Validate a candidate path against the directed graph."""
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

    if (
        candidate_length is not None
        and ground_truth_length is not None
        and ground_truth_length > 0
    ):
        absolute_length_error = abs(candidate_length - ground_truth_length)
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

    if (
        declared_length is not None
        and computed_length is not None
        and computed_length > 0
    ):
        absolute_error = abs(declared_length - computed_length)
        relative_error = absolute_error / computed_length

    return {
        "declared_length_absolute_error": absolute_error,
        "declared_length_relative_error": relative_error,
    }
