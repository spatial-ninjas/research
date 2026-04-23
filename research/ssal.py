from __future__ import annotations

from collections import defaultdict
import math
from typing import Any

import geopandas as gpd


def safe_float(value: Any) -> float | None:
    """Convert a value to float, returning None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_oneway(value: Any) -> bool:
    """Parse common truthy/falsy representations for OSM oneway values."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def load_layers(gpkg_path: str, edges_layer: str, nodes_layer: str):
    """Load edge and node layers from a GeoPackage file."""
    edges = gpd.read_file(gpkg_path, layer=edges_layer)
    nodes = gpd.read_file(gpkg_path, layer=nodes_layer)
    return edges, nodes


def build_node_map(nodes_gdf, node_id_col: str = "osmid") -> dict[str, dict[str, float | None]]:
    """Build a node lookup map containing x/y coordinates by node id."""
    node_map: dict[str, dict[str, float | None]] = {}

    for _, row in nodes_gdf.iterrows():
        node_id = str(row[node_id_col])
        node_map[node_id] = {
            "x": safe_float(row.get("x")),
            "y": safe_float(row.get("y")),
        }

    return node_map


def calculate_bearing(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate bearing in degrees from point 1 to point 2."""
    dx = x2 - x1
    dy = y2 - y1

    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)

    return (angle_deg + 360) % 360


def bearing_to_cardinal(bearing: float) -> str:
    """Convert a bearing in degrees to an 8-way cardinal direction."""
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int((bearing + 22.5) // 45) % 8]


def build_adjacency_from_edges(
    edges_gdf,
    node_map: dict[str, dict[str, float | None]] | None = None,
    u_col: str = "u",
    v_col: str = "v",
    attr_map: dict[str, str] | None = None,
    include_coords: bool = False,
    include_direction: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    """
    Build an adjacency mapping from edge data.

    Each node maps to a list of neighbor edge descriptors.
    """
    if attr_map is None:
        attr_map = {
            "length": "length",
            "name": "name",
            "oneway": "oneway",
        }

    adj: dict[str, dict[tuple[Any, ...], dict[str, Any]]] = defaultdict(dict)

    for _, row in edges_gdf.iterrows():
        u = str(row[u_col])
        v = str(row[v_col])

        attrs: dict[str, Any] = {}
        for key, col in attr_map.items():
            val = row.get(col, None)
            if val in [None, "NULL", ""]:
                continue
            attrs[key] = val

        length_val = safe_float(attrs.get("length"))
        length = round(length_val, 1) if length_val is not None else 0.0
        name = attrs.get("name", "unknown")
        oneway = parse_oneway(attrs.get("oneway", False))

        extra: dict[str, Any] = {}

        has_node_coords = (
            node_map is not None
            and u in node_map
            and v in node_map
        )

        if has_node_coords:
            x1, y1 = node_map[u]["x"], node_map[u]["y"]
            x2, y2 = node_map[v]["x"], node_map[v]["y"]

            if include_coords:
                extra.update(
                    {
                        "from_x": x1,
                        "from_y": y1,
                        "to_x": x2,
                        "to_y": y2,
                    }
                )

            if include_direction and None not in [x1, y1, x2, y2]:
                bearing = calculate_bearing(x1, y1, x2, y2)
                extra["dir"] = bearing_to_cardinal(bearing)

        data = {
            "to": v,
            "length": length,
            "name": name,
            "oneway": oneway,
            **extra,
        }

        key_fwd = (v, length, name, oneway)
        adj[u][key_fwd] = data

        if not oneway:
            rev_data = data.copy()

            if include_direction and "dir" in rev_data:
                opposite = {
                    "N": "S",
                    "NE": "SW",
                    "E": "W",
                    "SE": "NW",
                    "S": "N",
                    "SW": "NE",
                    "W": "E",
                    "NW": "SE",
                }
                rev_data["dir"] = opposite.get(rev_data["dir"])

            adj[v][(u, length, name, oneway)] = {
                **rev_data,
                "to": u,
            }

    return {node: list(neighbors.values()) for node, neighbors in adj.items()}


def format_ssal_compact(
    adj: dict[str, list[dict[str, Any]]],
    include: list[str] | None = None,
) -> str:
    """
    Format adjacency data into the compact SSAL text representation.

    Output ordering is stabilized by sorting nodes and neighbors.
    """
    if include is None:
        include = ["length", "name", "oneway"]

    lines: list[str] = []

    for node in sorted(adj.keys()):
        lines.append(f"{node}:")

        neighbors = sorted(
            adj[node],
            key=lambda n: (
                str(n.get("to", "")),
                str(n.get("name", "")),
                float(n.get("length", 0)),
            ),
        )

        for neighbor in neighbors:
            parts: list[str] = []

            for key in include:
                if key not in neighbor:
                    continue

                val = neighbor[key]

                if val is None:
                    continue

                if key == "length":
                    parts.append(f"{val}")
                elif key == "oneway":
                    parts.append("1w" if val else "2w")
                elif key == "dir":
                    parts.append(str(val))
                elif key in ["from_x", "from_y", "to_x", "to_y"]:
                    parts.append(f"{key}={round(val, 5)}")
                else:
                    parts.append(str(val))

            token = ", ".join(parts)
            lines.append(f"  {neighbor['to']} {{{token}}}")

    return "\n".join(lines)


def gpkg_to_ssal(
    gpkg_path: str,
    edges_layer: str,
    nodes_layer: str,
    u_col: str = "u",
    v_col: str = "v",
    node_id_col: str = "osmid",
    attr_map: dict[str, str] | None = None,
    include_attrs: list[str] | None = None,
    include_coords: bool = False,
    include_direction: bool = False,
) -> str:
    """Convert a GeoPackage road network into compact SSAL text."""
    edges, nodes = load_layers(gpkg_path, edges_layer, nodes_layer)

    node_map = build_node_map(nodes, node_id_col=node_id_col)

    adj = build_adjacency_from_edges(
        edges,
        node_map=node_map,
        u_col=u_col,
        v_col=v_col,
        attr_map=attr_map,
        include_coords=include_coords,
        include_direction=include_direction,
    )

    return format_ssal_compact(adj, include=include_attrs)
