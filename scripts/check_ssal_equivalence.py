from __future__ import annotations

import argparse
import ast
from collections import Counter
from pathlib import Path


def parse_ssal(path: Path) -> dict[int, list[tuple[int, tuple[str, ...]]]]:
    """
    Parse a compact SSAL text file into a normalized in-memory structure.

    Returns:
        {
            node_id: [
                (to_node_id, (attr1, attr2, ...)),
                ...
            ],
            ...
        }
    """
    graph: dict[int, list[tuple[int, tuple[str, ...]]]] = {}
    current_node: int | None = None

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if not stripped:
                continue

            if not line.startswith("  "):
                current_node = int(stripped[:-1])
                graph[current_node] = []
                continue

            if current_node is None:
                raise ValueError(f"Neighbor line encountered before any node header in {path}")

            left, right = stripped.split(" {", 1)
            to_node = int(left)
            attrs = tuple(part.strip() for part in right[:-1].split(","))  # drop trailing "}"
            graph[current_node].append((to_node, attrs))

    return graph


def edge_count(graph: dict[int, list[tuple[int, tuple[str, ...]]]]) -> int:
    return sum(len(neighbors) for neighbors in graph.values())


def split_edge(edge: tuple[int, tuple[str, ...]]) -> tuple[int, str | None, tuple[str, ...]]:
    """
    Split an edge into:
      - destination node
      - street name if present
      - remaining attributes excluding name

    Assumes SSAL edge attrs look roughly like:
      (length, name, oneway, dir)
    but keeps logic tolerant to shorter tuples.
    """
    to_node, attrs = edge
    name = attrs[1] if len(attrs) >= 2 else None
    remainder = tuple(attr for i, attr in enumerate(attrs) if i != 1)
    return to_node, name, remainder


def canonical_edges(
    graph: dict[int, list[tuple[int, tuple[str, ...]]]],
    ignore_names: bool = False,
) -> dict[int, Counter]:
    """
    Build canonical per-node edge multisets.

    If ignore_names=True, street names are excluded from comparison.
    """
    result: dict[int, Counter] = {}

    for node, edges in graph.items():
        items = []
        for edge in edges:
            to_node, name, remainder = split_edge(edge)
            if ignore_names:
                items.append((to_node, remainder))
            else:
                items.append((to_node, name, remainder))
        result[node] = Counter(items)

    return result


def compare_order(old_graph: dict[int, list], new_graph: dict[int, list]) -> tuple[bool, list[int], list[int]]:
    old_order = list(old_graph.keys())
    new_order = list(new_graph.keys())
    return old_order == new_order, old_order[:10], new_order[:10]


def compare_structure(
    old_graph: dict[int, list[tuple[int, tuple[str, ...]]]],
    new_graph: dict[int, list[tuple[int, tuple[str, ...]]]],
) -> tuple[list[int], list[int]]:
    """
    Returns:
      - nodes with any edge-level difference
      - nodes with non-name structural difference
    """
    old_full = canonical_edges(old_graph, ignore_names=False)
    new_full = canonical_edges(new_graph, ignore_names=False)

    old_noname = canonical_edges(old_graph, ignore_names=True)
    new_noname = canonical_edges(new_graph, ignore_names=True)

    all_nodes = sorted(set(old_graph) | set(new_graph))

    any_diff_nodes: list[int] = []
    nonname_diff_nodes: list[int] = []

    for node in all_nodes:
        if old_full.get(node, Counter()) != new_full.get(node, Counter()):
            any_diff_nodes.append(node)
        if old_noname.get(node, Counter()) != new_noname.get(node, Counter()):
            nonname_diff_nodes.append(node)

    return any_diff_nodes, nonname_diff_nodes


def collect_name_changes(
    old_graph: dict[int, list[tuple[int, tuple[str, ...]]]],
    new_graph: dict[int, list[tuple[int, tuple[str, ...]]]],
) -> Counter[tuple[str, str]]:
    """
    Count name-only changes when structure excluding names is the same.
    """
    changes: Counter[tuple[str, str]] = Counter()

    shared_nodes = sorted(set(old_graph) & set(new_graph))

    for node in shared_nodes:
        old_edges = old_graph[node]
        new_edges = new_graph[node]

        old_grouped: dict[tuple[int, tuple[str, ...]], list[str | None]] = {}
        new_grouped: dict[tuple[int, tuple[str, ...]], list[str | None]] = {}

        for edge in old_edges:
            to_node, name, remainder = split_edge(edge)
            old_grouped.setdefault((to_node, remainder), []).append(name)

        for edge in new_edges:
            to_node, name, remainder = split_edge(edge)
            new_grouped.setdefault((to_node, remainder), []).append(name)

        shared_keys = set(old_grouped) & set(new_grouped)

        for key in shared_keys:
            old_names = sorted(old_grouped[key], key=lambda x: "" if x is None else x)
            new_names = sorted(new_grouped[key], key=lambda x: "" if x is None else x)

            for old_name, new_name in zip(old_names, new_names):
                if old_name != new_name and old_name is not None and new_name is not None:
                    changes[(old_name, new_name)] += 1

    return changes


def print_report(old_path: Path, new_path: Path) -> int:
    old_graph = parse_ssal(old_path)
    new_graph = parse_ssal(new_path)

    old_nodes = len(old_graph)
    new_nodes = len(new_graph)
    old_edges = edge_count(old_graph)
    new_edges = edge_count(new_graph)

    old_node_set = set(old_graph)
    new_node_set = set(new_graph)

    same_node_set = old_node_set == new_node_set
    missing_from_new = sorted(old_node_set - new_node_set)
    missing_from_old = sorted(new_node_set - old_node_set)

    same_order, old_first10, new_first10 = compare_order(old_graph, new_graph)
    any_diff_nodes, nonname_diff_nodes = compare_structure(old_graph, new_graph)
    name_changes = collect_name_changes(old_graph, new_graph)

    print("=== BASIC STATS ===")
    print(f"old file: {old_path}")
    print(f"new file: {new_path}")
    print(f"old nodes: {old_nodes}")
    print(f"new nodes: {new_nodes}")
    print(f"old edges: {old_edges}")
    print(f"new edges: {new_edges}")
    print()

    print("=== NODE SET COMPARISON ===")
    print(f"same node-id set: {same_node_set}")
    print(f"missing from new: {len(missing_from_new)}")
    print(f"missing from old: {len(missing_from_old)}")
    if missing_from_new[:10]:
        print(f"first missing from new: {missing_from_new[:10]}")
    if missing_from_old[:10]:
        print(f"first missing from old: {missing_from_old[:10]}")
    print()

    print("=== ORDER CHECK ===")
    print(f"same top-level order: {same_order}")
    print(f"first 10 old: {old_first10}")
    print(f"first 10 new: {new_first10}")
    print()

    print("=== STRUCTURE CHECK ===")
    print(f"nodes with any edge-level difference: {len(any_diff_nodes)}")
    print(f"nodes with non-name structural difference: {len(nonname_diff_nodes)}")
    if nonname_diff_nodes[:10]:
        print(f"first non-name diff nodes: {nonname_diff_nodes[:10]}")
    else:
        print("No structural differences apart from possible street-name changes.")
    print()

    print("=== NAME-ONLY CHANGES ===")
    if name_changes:
        for (old_name, new_name), count in name_changes.most_common():
            print(f"{old_name!r} -> {new_name!r}: {count} edge(s)")
    else:
        print("No name-only changes found.")
    print()

    print("=== VERDICT ===")
    if old_nodes != new_nodes or old_edges != new_edges or not same_node_set or nonname_diff_nodes:
        print("Graph structure differs.")
        return 1

    if not same_order or name_changes:
        print("Same graph structure. Differences are reordering + street-name normalization.")
        return 0

    print("Files are structurally identical.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two SSAL files for structural equivalence."
    )
    parser.add_argument("old_file", type=Path, help="Path to the old/reference SSAL file")
    parser.add_argument("new_file", type=Path, help="Path to the new/generated SSAL file")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return print_report(args.old_file, args.new_file)


if __name__ == "__main__":
    raise SystemExit(main())
