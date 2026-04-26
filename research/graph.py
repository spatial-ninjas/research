from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
