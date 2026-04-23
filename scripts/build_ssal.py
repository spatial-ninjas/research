from pathlib import Path
import sys
import argparse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.ssal import gpkg_to_ssal

DEFAULT_GPKG_PATH = "data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg"
DEFAULT_OUTPUT_PATH = "data/derived/ssal/ssal_osm_southern_helsinki_slimmed_cropped.txt"
DEFAULT_EDGES_LAYER = "slimmed_cropped_edges"
DEFAULT_NODES_LAYER = "slimmed_cropped_nodes"
DEFAULT_INCLUDE_ATTRS = ["length", "name", "oneway", "from_x", "from_y", "to_x", "to_y"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a compact SSAL text artifact from a GeoPackage road network."
    )
    parser.add_argument(
        "--gpkg-path",
        default=DEFAULT_GPKG_PATH,
        help=f"Path to GeoPackage input (default: {DEFAULT_GPKG_PATH})",
    )
    parser.add_argument(
        "--edges-layer",
        default=DEFAULT_EDGES_LAYER,
        help=f"GeoPackage edges layer name (default: {DEFAULT_EDGES_LAYER})",
    )
    parser.add_argument(
        "--nodes-layer",
        default=DEFAULT_NODES_LAYER,
        help=f"GeoPackage nodes layer name (default: {DEFAULT_NODES_LAYER})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output SSAL text path (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--include-direction",
        action="store_true",
        help="Include 8-way cardinal direction in the SSAL output.",
    )
    parser.add_argument(
        "--include-coords",
        action="store_true",
        default=True,
        help="Include explicit coordinate fields in the SSAL output (default: enabled).",
    )
    parser.add_argument(
        "--no-include-coords",
        dest="include_coords",
        action="store_false",
        help="Disable explicit coordinate fields in the SSAL output.",
    )
    parser.add_argument(
        "--include-attrs",
        nargs="+",
        default=DEFAULT_INCLUDE_ATTRS,
        help="Attributes to include in SSAL output "
             "(default: length name oneway from_x from_y to_x to_y)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ssal = gpkg_to_ssal(
        gpkg_path=args.gpkg_path,
        edges_layer=args.edges_layer,
        nodes_layer=args.nodes_layer,
        include_direction=args.include_direction,
        include_coords=args.include_coords,
        include_attrs=args.include_attrs,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ssal, encoding="utf-8")

    print(f"SSAL written to: {output_path}")
    print(f"Edges layer: {args.edges_layer}")
    print(f"Nodes layer: {args.nodes_layer}")
    print(f"Included attrs: {args.include_attrs}")
    print(f"Include direction: {args.include_direction}")
    print(f"Include coords: {args.include_coords}")


if __name__ == "__main__":
    main()
