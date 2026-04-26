"""Graph utilities for SSAL-native route evaluation.

This module converts compact SSAL text into a small directed graph and provides
Dijkstra shortest-path search over that graph. The goal is to compute ground
truth from the same SSAL representation that is shown to the LLM, avoiding
mismatches with external routing services.

The graph treats every SSAL neighbor entry as a directed edge. Reverse edges are
not inferred here; bidirectional roads should already be represented by the SSAL
generation step as two directed adjacency entries.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import re
from typing import Any


_NODE_RE = re.compile(r"^(\S+):\s*$")
_EDGE_RE = re.compile(r"^\s+(\S+)\s+\{(.*)\}\s*$")


@dataclass(frozen=True)
class Edge:
    """Directed edge parsed from SSAL."""

    source: str
    target: str
    length: float
    name: str | None = None
    direction: str | None = None
    attrs: dict[str, Any] | None = None


@dataclass
class Graph:
    """Small directed graph representation used for SSAL-native evaluation."""

    adjacency: dict[str, list[Edge]]

    def nodes(self) -> list[str]:
        """Return sorted node IDs for deterministic UI display and tests."""
        return sorted(self.adjacency.keys())

    def has_node(self, node: str) -> bool:
        return node in self.adjacency

    def get_edge(self, source: str, target: str) -> Edge | None:
        """Return a directed edge only if it exists exactly as source -> target."""
        for edge in self.adjacency.get(source, []):
            if edge.target == target:
                return edge
        return None

    def has_edge(self, source: str, target: str) -> bool:
        return self.get_edge(source, target) is not None

    def path_length(self, path: list[str]) -> float:
        """Compute path length from graph edges instead of trusting model output."""        
        if len(path) < 2:
            return 0.0

        total = 0.0

        for source, target in zip(path, path[1:]):
            edge = self.get_edge(source, target)
            if edge is None:
                raise ValueError(f"No edge from {source} to {target}")
            total += edge.length

        return total


def parse_edge_attrs(raw_attrs: str) -> dict[str, Any]:
    """Parse the comma-separated metadata inside an SSAL edge block.

    The first three positional fields follow the compact SSAL convention:
    length, street/name, and direction marker. Additional key=value fields
    are preserved so later code can use coordinates or other exported metadata.
    """

    parts = [part.strip() for part in raw_attrs.split(",")]
    attrs: dict[str, Any] = {}

    if parts and parts[0]:
        try:
            attrs["length"] = float(parts[0])
        except ValueError:
            raise ValueError(f"Invalid edge length: {parts[0]!r}")

    if len(parts) >= 2 and parts[1]:
        attrs["name"] = parts[1]

    if len(parts) >= 3 and parts[2]:
        attrs["direction"] = parts[2]

    for part in parts[3:]:
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()

        try:
            attrs[key] = float(value)
        except ValueError:
            attrs[key] = value

    return attrs


def build_graph_from_ssal(ssal_text: str) -> Graph:
    """Build a directed graph from compact SSAL text.

    Reverse edges are not inferred here. If a road is traversable in both
    directions, the SSAL generation step should already have emitted both
    adjacency entries.
    """

    adjacency: dict[str, list[Edge]] = {}
    current_node: str | None = None

    for line_number, line in enumerate(ssal_text.splitlines(), start=1):
        if not line.strip():
            continue

        node_match = _NODE_RE.match(line)
        if node_match:
            current_node = node_match.group(1)
            adjacency.setdefault(current_node, [])
            continue

        edge_match = _EDGE_RE.match(line)
        if edge_match:
            if current_node is None:
                raise ValueError(
                    f"Edge appears before any source node at line {line_number}: {line!r}"
                )

            target = edge_match.group(1)
            attrs = parse_edge_attrs(edge_match.group(2))

            if "length" not in attrs:
                raise ValueError(
                    f"Missing edge length at line {line_number}: {line!r}"
                )

            edge = Edge(
                source=current_node,
                target=target,
                length=float(attrs["length"]),
                name=attrs.get("name"),
                direction=attrs.get("direction"),
                attrs=attrs,
            )

            adjacency.setdefault(current_node, []).append(edge)
            
            # Target-only nodes still need to exist so they can be valid
            # destinations and can be distinguished from unknown node IDs.
            adjacency.setdefault(target, [])
            continue

        raise ValueError(f"Could not parse SSAL line {line_number}: {line!r}")

    return Graph(adjacency=adjacency)


def dijkstra_shortest_path(
    graph: Graph,
    origin: str,
    destination: str,
) -> dict[str, Any]:
    """Return the shortest path using edge lengths from the SSAL-derived graph.

    The result is a plain dictionary because the dashboard and evaluator can
    serialize it directly and display failure reasons without exception handling.
    """
    if origin not in graph.adjacency:
        return {
            "ok": False,
            "reason": "unknown_origin",
            "origin": origin,
            "destination": destination,
        }

    if destination not in graph.adjacency:
        return {
            "ok": False,
            "reason": "unknown_destination",
            "origin": origin,
            "destination": destination,
        }

    if origin == destination:
        return {
            "ok": True,
            "origin": origin,
            "destination": destination,
            "path": [origin],
            "total_length": 0.0,
        }

    distances: dict[str, float] = {origin: 0.0}
    previous: dict[str, str | None] = {origin: None}

    # Heap entries are ordered by (distance, node_id). This gives deterministic
    # equal-distance frontier expansion using lexicographic node ID order.
    queue: list[tuple[float, str]] = [(0.0, origin)]

    while queue:
        current_distance, node = heapq.heappop(queue)

        if node == destination:
            break

        if current_distance > distances.get(node, float("inf")):
            continue

        for edge in graph.adjacency.get(node, []):
            if edge.length < 0:
                raise ValueError(
                    f"Dijkstra cannot handle negative edge length: "
                    f"{edge.source} -> {edge.target} = {edge.length}"
                )

            new_distance = current_distance + edge.length

            if new_distance < distances.get(edge.target, float("inf")):
                distances[edge.target] = new_distance
                previous[edge.target] = node
                heapq.heappush(queue, (new_distance, edge.target))

    if destination not in distances:
        return {
            "ok": False,
            "reason": "no_path",
            "origin": origin,
            "destination": destination,
        }

    path: list[str] = []
    node: str | None = destination

    while node is not None:
        path.append(node)
        node = previous[node]

    path.reverse()

    return {
        "ok": True,
        "origin": origin,
        "destination": destination,
        "path": path,
        "total_length": distances[destination],
    }
