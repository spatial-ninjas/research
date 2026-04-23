import argparse
import json
import os
import re
from collections import Counter, defaultdict
from typing import Any

from dotenv import load_dotenv
import geopandas as gpd
import numpy as np
from routingpy.routers import ORS

load_dotenv()

DEFAULT_GPKG_PATH = "data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg"
DEFAULT_HISTORY_JSON = "data/raw/llm_history_exports/llm_compare_history_2026-04-20.json"
DEFAULT_NODES_LAYER = "slimmed_cropped_nodes"


def clean_json(text: str) -> str | None:
    """Extract the first JSON object-like block from model text output."""
    if not text or not isinstance(text, str):
        return None

    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None


def looks_like_routing_prompt(prompt: str) -> bool:
    """Heuristic to skip unrelated dashboard history entries."""
    if not prompt:
        return False

    prompt_lower = prompt.lower()
    routing_markers = [
        "ssal",
        "routing engine",
        "origin node",
        "destination node",
        "shortest path",
        "one-way",
        "1w",
        "2w",
    ]
    return any(marker in prompt_lower for marker in routing_markers)


def load_node_lookup(gpkg_path: str, nodes_layer: str) -> dict[str, list[float]]:
    """Load node coordinates keyed by OSM node id."""
    nodes_gdf = gpd.read_file(gpkg_path, layer=nodes_layer)
    return {
        str(row["osmid"]): [float(row["x"]), float(row["y"])]
        for _, row in nodes_gdf.iterrows()
    }


def load_history(history_json_path: str) -> list[dict[str, Any]]:
    """Load exported dashboard history JSON."""
    with open(history_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("History JSON must contain a list of entries")
    return data


def classify_skip_reason(entry: dict[str, Any], json_str: str | None) -> str | None:
    """
    Classify obvious non-evaluable cases before json.loads.
    Returns a skip reason string or None if processing should continue.
    """
    finish_status = entry.get("finish_status")
    raw_text = entry.get("response_text") or entry.get("response") or entry.get("text") or ""
    error_text = entry.get("error_text")

    if error_text and not raw_text:
        return "provider_error"

    if not json_str:
        if finish_status == "MAX_TOKENS":
            return "cropped_json"
        return "no_json"

    return None


def evaluate_entry(
    entry: dict[str, Any],
    node_lookup: dict[str, list[float]],
    client: ORS,
) -> dict[str, Any]:
    """Evaluate a single routing history entry and return computed metrics."""
    model_id = entry.get("id")
    provider = entry.get("provider", "unknown")
    model = entry.get("model", "unknown")
    finish_status = entry.get("finish_status")
    max_output_tokens = entry.get("max_output_tokens")
    raw_text = entry.get("response_text") or entry.get("response") or entry.get("text") or ""

    json_str = clean_json(str(raw_text))
    preclassified = classify_skip_reason(entry, json_str)
    if preclassified is not None:
        return {
            "status": "skipped",
            "reason": preclassified,
            "model_id": model_id,
            "provider": provider,
            "model": model,
            "finish_status": finish_status,
            "max_output_tokens": max_output_tokens,
        }

    try:
        res = json.loads(json_str)

        path = res.get("path") or res.get("route")
        origin = str(res.get("origin", "")).strip()
        destination = str(res.get("destination", "")).strip()

        if not path:
            return {
                "status": "skipped",
                "reason": "missing_path",
                "model_id": model_id,
                "provider": provider,
                "model": model,
                "finish_status": finish_status,
                "max_output_tokens": max_output_tokens,
            }

        if origin not in node_lookup or destination not in node_lookup:
            return {
                "status": "skipped",
                "reason": "missing_node_lookup",
                "model_id": model_id,
                "provider": provider,
                "model": model,
                "finish_status": finish_status,
                "max_output_tokens": max_output_tokens,
                "origin": origin,
                "destination": destination,
            }

        locations = [node_lookup[origin], node_lookup[destination]]
        route = client.directions(locations=locations, profile="driving-car")

        llm_coords = []
        for step in path:
            nid = str(step.get("node", "")).strip()
            if nid in node_lookup:
                llm_coords.append([float(c) for c in node_lookup[nid]])

        gt_coords = np.array(route.geometry, dtype=float)
        llm_coords_arr = np.array(llm_coords, dtype=float)

        node_accuracy = 0.0
        if len(llm_coords_arr) > 0 and len(gt_coords) > 0:
            min_len = min(len(llm_coords_arr), len(gt_coords))
            matches = [
                np.allclose(llm_coords_arr[j], gt_coords[j], atol=1e-4)
                for j in range(min_len)
            ]
            node_accuracy = sum(matches) / max(len(llm_coords_arr), len(gt_coords))

        try:
            llm_distance = float(res.get("total_length", 0))
            gt_distance = float(route.distance)
            dist_precision = (
                max(0, 1 - (abs(llm_distance - gt_distance) / gt_distance))
                if gt_distance > 0
                else 0.0
            )
        except (ValueError, TypeError):
            llm_distance = 0.0
            gt_distance = float(route.distance)
            dist_precision = 0.0

        return {
            "status": "evaluated",
            "model_id": model_id,
            "provider": provider,
            "model": model,
            "finish_status": finish_status,
            "max_output_tokens": max_output_tokens,
            "origin": origin,
            "destination": destination,
            "node_accuracy": node_accuracy,
            "dist_precision": dist_precision,
            "llm_distance": llm_distance,
            "gt_distance": gt_distance,
        }

    except json.JSONDecodeError as e:
        return {
            "status": "skipped",
            "reason": "cropped_json",
            "model_id": model_id,
            "provider": provider,
            "model": model,
            "finish_status": finish_status,
            "max_output_tokens": max_output_tokens,
            "error": str(e),
        }
    except Exception as e:
        return {
            "status": "skipped",
            "reason": "other_processing_error",
            "model_id": model_id,
            "provider": provider,
            "model": model,
            "finish_status": finish_status,
            "max_output_tokens": max_output_tokens,
            "error": str(e),
        }


def print_evaluation_result(result: dict[str, Any]) -> None:
    """Print one evaluated entry."""
    print(
        f"\n--- Evaluation for Model ID: {result['model_id']} "
        f"({result['provider']} / {result['model']}) ---"
    )
    print(f"Route: {result['origin']} -> {result['destination']}")
    print(
        f"Finish status: {result.get('finish_status')} | "
        f"Max output tokens: {result.get('max_output_tokens')}"
    )
    print(f"Node Sequence Accuracy: {result['node_accuracy'] * 100:.1f}%")
    print(f"Distance Precision:    {result['dist_precision'] * 100:.1f}%")
    print(
        f"Length Comparison: LLM {result['llm_distance']}m | "
        f"Algorithm {result['gt_distance']:.1f}m"
    )


def print_skip_result(result: dict[str, Any]) -> None:
    """Print one skipped entry when it is informative."""
    reason = result["reason"]
    model_id = result.get("model_id")
    provider = result.get("provider", "unknown")
    model = result.get("model", "unknown")

    if reason == "cropped_json":
        print(
            f"Skipped Model ID {model_id} ({provider} / {model}): "
            f"incomplete or cropped JSON response"
        )
    elif reason == "provider_error":
        print(
            f"Skipped Model ID {model_id} ({provider} / {model}): "
            f"provider error with no usable response text"
        )


def summarize_results(
    total_entries: int,
    routing_entries: int,
    results: list[dict[str, Any]],
    model_counts: Counter,
) -> None:
    """Print run-level and per-model summary statistics."""
    evaluated_entries = sum(1 for r in results if r["status"] == "evaluated")
    skip_counts = Counter(r["reason"] for r in results if r["status"] == "skipped")

    evaluated_by_model = Counter()
    skipped_by_model = Counter()
    results_by_model = defaultdict(list)

    for result in results:
        model_key = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
        if result["status"] == "evaluated":
            evaluated_by_model[model_key] += 1
            results_by_model[model_key].append(result)
        else:
            skipped_by_model[model_key] += 1

    print("\n--- Run Summary ---")
    print(f"Total history entries:        {total_entries}")
    print(f"Routing-related entries:      {routing_entries}")
    print(f"Successfully evaluated:       {evaluated_entries}")

    for reason, count in sorted(skip_counts.items()):
        print(f"Skipped ({reason}):".ljust(30) + f"{count}")

    print("\n--- Per Model Summary ---")
    for model_key in sorted(model_counts.keys()):
        evaluated = evaluated_by_model.get(model_key, 0)
        skipped = skipped_by_model.get(model_key, 0)
        print(model_key)
        print(f"  total seen:   {model_counts[model_key]}")
        print(f"  evaluated:    {evaluated}")
        print(f"  skipped:      {skipped}")

        model_results = results_by_model.get(model_key, [])
        if model_results:
            avg_node = sum(r["node_accuracy"] for r in model_results) / len(model_results)
            avg_dist = sum(r["dist_precision"] for r in model_results) / len(model_results)
            print(f"  avg node accuracy:   {avg_node * 100:.1f}%")
            print(f"  avg distance prec.:  {avg_dist * 100:.1f}%")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate routing-model outputs from dashboard export history."
    )
    parser.add_argument(
        "--gpkg-path",
        default=os.getenv("GPKG_PATH", DEFAULT_GPKG_PATH),
        help="Path to GeoPackage file "
             f"(default: env GPKG_PATH or {DEFAULT_GPKG_PATH})",
    )
    parser.add_argument(
        "--history-json",
        default=os.getenv("HISTORY_JSON", DEFAULT_HISTORY_JSON),
        help="Path to exported history JSON "
             f"(default: env HISTORY_JSON or {DEFAULT_HISTORY_JSON})",
    )
    parser.add_argument(
        "--nodes-layer",
        default=os.getenv("NODES_LAYER", DEFAULT_NODES_LAYER),
        help="GeoPackage layer name for nodes "
             f"(default: env NODES_LAYER or {DEFAULT_NODES_LAYER})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ors_api_key = os.getenv("ORS_API_KEY")
    if not ors_api_key:
        raise RuntimeError("Missing ORS_API_KEY environment variable")

    client = ORS(api_key=ors_api_key)

    print("Step 1: Loading network data...")
    try:
        node_lookup = load_node_lookup(args.gpkg_path, args.nodes_layer)
        print(f"Status: Successfully loaded {len(node_lookup)} nodes.")
    except Exception as e:
        print(f"Critical Error: Failed to load GeoPackage. {e}")
        return

    print("\nStep 2: Processing model history...")
    try:
        history = load_history(args.history_json)
    except Exception as e:
        print(f"Critical Error: Failed to load history file. {e}")
        return

    total_entries = 0
    routing_entries = 0
    results: list[dict[str, Any]] = []
    model_counts = Counter()

    for i, entry in enumerate(history):
        total_entries += 1
        provider = entry.get("provider", "unknown")
        model = entry.get("model", "unknown")
        model_key = f"{provider}:{model}"
        model_counts[model_key] += 1

        prompt = entry.get("prompt") or ""
        if not looks_like_routing_prompt(prompt):
            results.append(
                {
                    "status": "skipped",
                    "reason": "non_routing_entry",
                    "model_id": entry.get("id", i),
                    "provider": provider,
                    "model": model,
                }
            )
            continue

        routing_entries += 1
        result = evaluate_entry(entry, node_lookup, client)
        results.append(result)

        if result["status"] == "evaluated":
            print_evaluation_result(result)
        else:
            print_skip_result(result)

    summarize_results(total_entries, routing_entries, results, model_counts)


if __name__ == "__main__":
    main()
