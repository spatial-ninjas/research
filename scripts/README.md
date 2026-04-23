# scripts

Utility scripts for evaluating routing-model outputs against the Helsinki routing network artifacts versioned in this repository.

## Current script

### `evaluate_history.py`

Evaluates routing-model outputs exported from `llm-compare-dashboard`.

It currently:

- loads node coordinates from the GeoPackage network
- reads a dashboard history export JSON
- filters to routing-related entries
- extracts model JSON outputs when possible
- compares model outputs against an OpenRouteService reference route
- reports per-entry results and run-level summaries

## Setup

Create and activate a virtual environment first.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

The evaluator reads configuration from a repo-root `.env` file and also supports CLI overrides.

You can copy from `.env.example`.

Example `.env`:

```dotenv
ORS_API_KEY=your_ors_api_key_here
GPKG_PATH=data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg
HISTORY_JSON=data/raw/llm_history_exports/llm_compare_history_2026-04-20.json
NODES_LAYER=slimmed_cropped_nodes
```

Required:

- `ORS_API_KEY`

Create an account on [openrouteservice.org](https://openrouteservice.org/) if needed.
The API key can be managed at [account.heigit.org/manage/key](https://account.heigit.org/manage/key).

Optional:

- `GPKG_PATH`
- `HISTORY_JSON`
- `NODES_LAYER`

## Running the evaluator

### Default run

```bash
python scripts/evaluate_history.py
```

This uses:

- CLI arguments if provided
- otherwise environment variables from `.env`
- otherwise built-in defaults for paths and layer names

You can also view all available options with:

```bash
python scripts/evaluate_history.py --help
```

### Override history JSON from CLI

```bash
python scripts/evaluate_history.py \
  --history-json data/raw/llm_history_exports/llm_compare_history_2026-04-16.json
```

### Override all main inputs from CLI

```bash
python scripts/evaluate_history.py \
  --gpkg-path data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg \
  --history-json data/raw/llm_history_exports/llm_compare_history_2026-04-20.json \
  --nodes-layer slimmed_cropped_nodes
```

## Notes

- The evaluator currently uses an approximate exploratory node-sequence comparison against OpenRouteService route geometry.
- This is useful for rough comparison, but it is not yet a fully graph-native path-equivalence metric.
- Some history entries may be skipped because the exported model response contains no JSON, cropped JSON, provider errors, or a non-routing prompt.
