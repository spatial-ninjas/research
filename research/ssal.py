import geopandas as gpd
from collections import defaultdict


def load_layers(gpkg_path, edges_layer, nodes_layer):
    edges = gpd.read_file(gpkg_path, layer=edges_layer)
    nodes = gpd.read_file(gpkg_path, layer=nodes_layer)
    return edges, nodes


def build_node_map(nodes_gdf, node_id_col="osmid"):
    """
    Map node IDs -> coordinates (optional, mainly for validation/debug)
    """
    node_map = {}

    for _, row in nodes_gdf.iterrows():
        node_id = str(row[node_id_col])
        node_map[node_id] = {
            "x": row.get("x"),
            "y": row.get("y")
        }

    return node_map


def build_adjacency_from_edges(
    edges_gdf,
    u_col="u",
    v_col="v",
    attr_map=None
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

        attrs = {}
        for key, col in attr_map.items():
            val = row.get(col, None)
            if val in [None, "NULL", ""]:
                continue
            attrs[key] = val

        length = round(float(attrs.get("length", 0)), 1)
        name = attrs.get("name", "unknown")
        oneway = bool(attrs.get("oneway", False))

        # Unique key removes duplicates
        key_fwd = (v, length, name, oneway)

        adj[u][key_fwd] = {
            "to": v,
            "length": length,
            "name": name,
            "oneway": oneway
        }

        # reverse if not one-way
        if not oneway:
            key_rev = (u, length, name, oneway)

            adj[v][key_rev] = {
                "to": u,
                "length": length,
                "name": name,
                "oneway": oneway
            }

    # Back to list
    adj = {k: list(v.values()) for k, v in adj.items()}

    return adj


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
    include_attrs=None
):
    """
    Full pipeline
    """

    edges, nodes = load_layers(gpkg_path, edges_layer, nodes_layer)

    node_map = build_node_map(nodes, node_id_col=node_id_col)

    adj = build_adjacency_from_edges(
        edges,
        u_col=u_col,
        v_col=v_col,
        attr_map=attr_map
    )

    ssal = format_ssal_compact(adj, include=include_attrs)

    return ssal


"""    
# Run gpkg_to_ssal with this part

gpkg_path = "C:/Users/eemil/Downloads/osm_southern_helsinki_slimmed_cropped.gpkg"

ssal = gpkg_to_ssal(
    gpkg_path=gpkg_path,
    edges_layer="slimmed_cropped_edges",
    nodes_layer="slimmed_cropped_nodes",

    u_col="u",
    v_col="v",
    node_id_col="osmid",

    attr_map={
        "type": "highway",
        "length": "length",
        "name": "name",
        "oneway": "oneway",
        "speed": "maxspeed",
        "lanes": "lanes"
    },

    include_attrs=["length", "name", "oneway"]
)

print(ssal)
"""