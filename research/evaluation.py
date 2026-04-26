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
