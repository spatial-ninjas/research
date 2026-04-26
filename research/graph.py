from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


_NODE_RE = re.compile(r"^(\S+):\s*$")
_EDGE_RE = re.compile(r"^\s+(\S+)\s+\{(.*)\}\s*$")


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    length: float
    name: str | None = None
    direction: str | None = None
    attrs: dict[str, Any] | None = None


@dataclass
class Graph:
    adjacency: dict[str, list[Edge]]

    def nodes(self) -> list[str]:
        return sorted(self.adjacency.keys())

    def has_node(self, node: str) -> bool:
        return node in self.adjacency

    def get_edge(self, source: str, target: str) -> Edge | None:
        for edge in self.adjacency.get(source, []):
            if edge.target == target:
                return edge
        return None

    def has_edge(self, source: str, target: str) -> bool:
        return self.get_edge(source, target) is not None

    def path_length(self, path: list[str]) -> float:
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
            adjacency.setdefault(target, [])
            continue

        raise ValueError(f"Could not parse SSAL line {line_number}: {line!r}")

    return Graph(adjacency=adjacency)