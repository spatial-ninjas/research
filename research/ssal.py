import geopandas as gpd
from collections import defaultdict
import math


def load_layers(gpkg_path, edges_layer, nodes_layer):
    edges = gpd.read_file(gpkg_path, layer=edges_layer)
    nodes = gpd.read_file(gpkg_path, layer=nodes_layer)
    return edges, nodes

def build_node_map(nodes_gdf, node_id_col="osmid"):
    node_map = {}

    for _, row in nodes_gdf.iterrows():
        node_id = str(row[node_id_col])

        def safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        node_map[node_id] = {
            "x": safe_float(row.get("x")),
            "y": safe_float(row.get("y"))
        }

    return node_map


def calculate_bearing(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)

    return (angle_deg + 360) % 360


def bearing_to_cardinal(b):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int((b + 22.5) // 45) % 8]


def build_adjacency_from_edges(
    edges_gdf,
    node_map=None,
    u_col="u",
    v_col="v",
    attr_map=None,
    include_coords=False,
    include_direction=False
):
    if attr_map is None:
        attr_map = {
            "length": "length",
            "name": "name",
            "oneway": "oneway"
        }

    adj = defaultdict(dict)

    for _, row in edges_gdf.iterrows():
        u = str(row[u_col])
        v = str(row[v_col])

        # ---- attributes ----
        attrs = {}
        for key, col in attr_map.items():
            val = row.get(col, None)
            if val in [None, "NULL", ""]:
                continue
            attrs[key] = val

        length = round(float(attrs.get("length", 0)), 1)
        name = attrs.get("name", "unknown")
        oneway = bool(attrs.get("oneway", False))

        extra = {}

        # ---- coordinates ----
        if include_coords and node_map:
            if u in node_map and v in node_map:
                extra.update({
                    "from_x": node_map[u]["x"],
                    "from_y": node_map[u]["y"],
                    "to_x": node_map[v]["x"],
                    "to_y": node_map[v]["y"]
                })

        # ---- direction ----
        if include_direction and node_map:
            if u in node_map and v in node_map:
                x1, y1 = node_map[u]["x"], node_map[u]["y"]
                x2, y2 = node_map[v]["x"], node_map[v]["y"]

                if None not in [x1, y1, x2, y2]:
                    bearing = calculate_bearing(x1, y1, x2, y2)
                    extra["dir"] = bearing_to_cardinal(bearing)

        # ---- forward edge ----
        data = {
            "to": v,
            "length": length,
            "name": name,
            "oneway": oneway,
            **extra
        }

        key_fwd = (v, length, name, oneway)
        adj[u][key_fwd] = data

        # ---- reverse edge ----
        if not oneway:
            rev_data = data.copy()

            if include_direction and "dir" in rev_data:
                opposite = {
                    "N": "S", "NE": "SW", "E": "W", "SE": "NW",
                    "S": "N", "SW": "NE", "W": "E", "NW": "SE"
                }
                rev_data["dir"] = opposite.get(rev_data["dir"])

            adj[v][(u, length, name, oneway)] = {
                **rev_data,
                "to": u
            }

    return {k: list(v.values()) for k, v in adj.items()}


def format_ssal_compact(adj, include=None):
    if include is None:
        include = ["length", "name", "oneway"]

    lines = []

    for node, neighbors in adj.items():
        lines.append(f"{node}:")

        for n in neighbors:
            parts = []

            for key in include:
                if key not in n:
                    continue

                val = n[key]

                if key == "length":
                    parts.append(f"{val}")
                elif key == "oneway":
                    parts.append("1w" if val else "2w")
                elif key == "dir":
                    parts.append(val)
                elif key in ["from_x", "from_y", "to_x", "to_y"]:
                    parts.append(f"{key}={round(val, 5)}")
                else:
                    parts.append(str(val))

            token = ", ".join(parts)
            lines.append(f"  {n['to']} {{{token}}}")

    return "\n".join(lines)


def gpkg_to_ssal(
    gpkg_path,
    edges_layer,
    nodes_layer,
    u_col="u",
    v_col="v",
    node_id_col="osmid",
    attr_map=None,
    include_attrs=None,
    include_coords=False,
    include_direction=False
):
    edges, nodes = load_layers(gpkg_path, edges_layer, nodes_layer)

    node_map = build_node_map(nodes, node_id_col=node_id_col)

    adj = build_adjacency_from_edges(
        edges,
        node_map=node_map,
        u_col=u_col,
        v_col=v_col,
        attr_map=attr_map,
        include_coords=include_coords,
        include_direction=include_direction
    )

    return format_ssal_compact(adj, include=include_attrs)


# Run gpkg_to_ssal with this part
"""
gpkg_path = "C:/Users/eemil/Downloads/osm_southern_helsinki_slimmed_cropped.gpkg"

ssal = gpkg_to_ssal(
    gpkg_path=gpkg_path,
    edges_layer="slimmed_cropped_edges",
    nodes_layer="slimmed_cropped_nodes",
    include_direction=True,
    include_coords=False,
    include_attrs=["length","name", "oneway", "dir", "from_x", "from_y", "to_x", "to_y"]
)
print(ssal)
"""