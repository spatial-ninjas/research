"""CLI for offline route-history evaluation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.history_evaluation import (
    evaluate_entry_file,
    evaluate_history_file,
    format_results_json,
    summarize_results,
    write_results_json,
)

DEFAULT_GPKG_PATH = "data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg"
DEFAULT_EDGES_LAYER = "slimmed_cropped_edges"
DEFAULT_NODES_LAYER = "slimmed_cropped_nodes"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments without running evaluation."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate route-history entries with the shared "
            "SSAL-native evaluator."
        )
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--entry-json",
        help="Path to a JSON file containing one route history entry.",
    )
    input_group.add_argument(
        "--history-json",
        help="Path to a JSON file containing a bulk route history export.",
    )

    parser.add_argument(
        "--gpkg-path",
        default=os.getenv("GPKG_PATH", DEFAULT_GPKG_PATH),
        help=(
            "Path to GeoPackage file "
            f"(default: env GPKG_PATH or {DEFAULT_GPKG_PATH})."
        ),
    )
    parser.add_argument(
        "--edges-layer",
        default=os.getenv("EDGES_LAYER", DEFAULT_EDGES_LAYER),
        help=(
            "GeoPackage edge layer "
            f"(default: env EDGES_LAYER or {DEFAULT_EDGES_LAYER})."
        ),
    )
    parser.add_argument(
        "--nodes-layer",
        default=os.getenv("NODES_LAYER", DEFAULT_NODES_LAYER),
        help=(
            "GeoPackage node layer "
            f"(default: env NODES_LAYER or {DEFAULT_NODES_LAYER})."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the offline evaluation CLI and return a process exit code."""
    args = parse_args(argv)

    if args.entry_json is not None:
        result = evaluate_entry_file(
            entry_json_path=args.entry_json,
            gpkg_path=args.gpkg_path,
            edges_layer=args.edges_layer,
            nodes_layer=args.nodes_layer,
        )

        if args.output:
            write_results_json(args.output, result=result)
        else:
            print(format_results_json(result=result))

        return 0

    rows = evaluate_history_file(
        history_json_path=args.history_json,
        gpkg_path=args.gpkg_path,
        edges_layer=args.edges_layer,
        nodes_layer=args.nodes_layer,
    )
    summary = summarize_results(rows)

    if args.output:
        write_results_json(args.output, results=rows, summary=summary)
    else:
        print(format_results_json(results=rows, summary=summary))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
