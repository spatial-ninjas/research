# research

Research workspace for evaluating LLM routing behavior on a simplified street-network representation of Southern Helsinki.

This repository contains the **research and evaluation side** of the project: routing-network inputs, stable SSAL artifacts, exported experiment inputs, reusable evaluation utilities, and analysis scripts. The broader project compares GPT-family and Gemini-family models on routing tasks over an OpenStreetMap-derived Helsinki network, using a shared SSAL-native evaluator with Dijkstra ground truth over the generated graph representation.

## Relationship to [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard)

The project is split across two repositories:

- [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard): run prompts, compare OpenAI and Gemini outputs side by side, and store/export history
- [research](https://github.com/spatial-ninjas/research): prepare routing artifacts, version experiment inputs, and evaluate routing results

The dashboard can use this repository as a local editable Python package during development. This allows the dashboard to import reusable logic from `research` without copying code between repositories.

## Project scope

The project studies how LLMs handle route-generation tasks when given a compact graph-like representation of a real street network instead of a standard map UI. The current reference map is a selected area of Southern Helsinki derived from OpenStreetMap. The current evaluation focuses on GPT and Gemini models.

Main evaluation concerns:

- structured output correctness
- candidate node-sequence validity
- distance estimation quality
- shortest-path agreement against SSAL-derived Dijkstra ground truth
- robustness as route difficulty increases

## Current workflow

```text
GeoPackage
   ↓
SSAL text
   ↓
SSAL-derived graph
   ↓
Dijkstra ground truth
   ↓
shared route evaluator
   ↓
offline history evaluation helpers / CLI
```

Typical workflow:

1. Prepare an OSM-derived routing network.
2. Build the SSAL artifact from the GeoPackage input.
3. Run routing prompts in [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard).
4. Export the dashboard history as JSON.
5. Store the export in this repository.
6. Evaluate the results with the reusable helpers and CLI here.
7. Record summaries and notes for later review.

## Setup

Create and activate a virtual environment first.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For runtime-only usage, install:

```bash
python -m pip install -r requirements.txt
```

### Local editable install from the dashboard repo

This repository can also be installed as a local editable Python package. This is useful when working with the sibling [`llm-compare-dashboard`](https://github.com/spatial-ninjas/llm-compare-dashboard) repository, so the dashboard can import reusable research utilities without copying code.

Expected local folder layout:

```text
spatial-ninjas/
  research/
  llm-compare-dashboard/
```

From inside `llm-compare-dashboard`:

```bash
source .venv/bin/activate
pip install -e ../research
```

If `llm-compare-dashboard/requirements.txt` includes:

```txt
-e ../research
```

then running the dashboard dependency install is enough:

```bash
pip install -r requirements.txt
```

Verify the imports with:

```bash
python -c "from research.ssal import gpkg_to_ssal; print('ssal ok')"
python -c "from research.history_evaluation import evaluate_entry_file; print('history evaluation ok')"
```

The package name is `spatial-ninjas-research`, while the Python import path remains:

```python
from research.ssal import gpkg_to_ssal
```

Create a repo-root `.env` file if you want to override the default network inputs:

```dotenv
GPKG_PATH=data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg
EDGES_LAYER=slimmed_cropped_edges
NODES_LAYER=slimmed_cropped_nodes
```

See [scripts/README.md](scripts/README.md) for script-specific usage details.

## Core components

### SSAL conversion

The OSM road network is converted into a simplified semantic adjacency list to reduce token usage while keeping the routing structure that matters.

The reusable conversion logic lives in:

- [research/ssal.py](research/ssal.py)

The CLI entry point for regenerating the versioned SSAL artifact is:

- [scripts/build_ssal.py](scripts/build_ssal.py)

Stable generated SSAL text artifacts are intentionally versioned in this repo.

### SSAL graph and Dijkstra baseline

The SSAL-native graph layer lives in:

- [research/graph.py](research/graph.py)

It provides:

- immutable `Edge` objects
- directed `Graph` objects
- SSAL-to-graph parsing
- target-only node preservation
- path-length calculation
- deterministic Dijkstra shortest-path search

This graph layer is the baseline used by the evaluator. The default evaluation path no longer compares against an external routing service.

### Shared route-response evaluation

The shared route evaluator lives in:

- [research/evaluation.py](research/evaluation.py)

It handles:

- JSON recovery from model responses
- route path extraction
- model-declared route-length extraction
- candidate path validation against the SSAL-derived graph
- Dijkstra ground-truth comparison
- node and directed-edge overlap metrics
- candidate-length and declared-length error metrics

This module contains the core route-evaluation logic. Offline history evaluation and future dashboard integration should call into this shared evaluator instead of duplicating parsing or metric code.

### Network loading

Network loading lives in:

- [research/network_loader.py](research/network_loader.py)

It loads the GeoPackage network, generates SSAL text, computes the SSAL hash, and builds the graph used for evaluation.

The main container is `NetworkBundle`, which stores:

- GeoPackage path
- generated SSAL text
- SSAL hash
- SSAL-derived graph
- edge layer name
- node layer name

The graph used for evaluation is built from the generated SSAL text, not directly from the GeoPackage. This keeps the evaluated graph aligned with the representation shown to the model.

### Offline history evaluation

Dashboard/export history evaluation is handled by:

- [research/history_evaluation.py](research/history_evaluation.py)

This module adapts exported route-history rows into calls to the shared SSAL-native evaluator. It also provides:

- one-entry JSON loading
- bulk history JSON loading
- metadata preservation
- explicit origin/destination route-context extraction
- file-based one-entry and bulk evaluation wrappers
- bulk summary aggregation
- JSON output formatting and writing

The CLI entry point is intentionally thin:

- [scripts/evaluate_history.py](scripts/evaluate_history.py)

### Evaluation components

The current evaluation workflow is split between reusable helpers and CLI scripts:

- [research/history_evaluation.py](research/history_evaluation.py) adapts dashboard/export history rows into the shared evaluator, preserves metadata, evaluates one-entry or bulk history JSON files, summarizes results, and formats/writes JSON output
- [research/evaluation.py](research/evaluation.py) contains the shared route-response evaluator, including JSON recovery, path extraction, path validation, Dijkstra ground truth, and route metrics
- [research/network_loader.py](research/network_loader.py) loads the GeoPackage network, generates SSAL text, computes the SSAL hash, and builds the graph used for evaluation
- [research/graph.py](research/graph.py) contains the SSAL graph model and deterministic Dijkstra baseline
- [scripts/build_ssal.py](scripts/build_ssal.py) builds the compact SSAL text artifact from the GeoPackage road-network input
- [scripts/evaluate_history.py](scripts/evaluate_history.py) is the thin CLI wrapper around `research.history_evaluation`
- [scripts/README.md](scripts/README.md) documents script dependencies, configuration, and usage

### LLM routing prototype

An earlier prototype script feeds SSAL data and a routing prompt to an LLM and expects a route in JSON format. It is kept for historical reference and is not treated as the main current workflow.

Current location:

- [archive/prototypes/](archive/prototypes/)

### Comparison interface and history

The project also uses a comparison interface in the separate dashboard repo for side-by-side model testing and persisted history. That history is later exported and analyzed here.

## Repository layout

- `data/raw/routing_networks/` — OSM-derived GeoPackage inputs
- `data/derived/ssal/` — stable generated SSAL text artifacts
- `data/raw/llm_history_exports/` — exported dashboard history JSONs
- `research/` — reusable Python logic for SSAL conversion, graph utilities, network loading, route evaluation, and history-evaluation adapters
- `scripts/` — executable SSAL generation and evaluation scripts
- `results/summaries/` — experiment notes and summaries
- `archive/prototypes/` — older prototype scripts
- `tests/` — regression tests for graph, evaluation, network loading, history helpers, and CLI wiring

## Common commands

Build the default SSAL artifact:

```bash
python scripts/build_ssal.py
```

Evaluate a dashboard history export:

```bash
python scripts/evaluate_history.py \
  --history-json data/raw/llm_history_exports/llm_compare_history_2026-04-20.json \
  --output results/summaries/history_evaluation.json
```

Evaluate one exported history row:

```bash
python scripts/evaluate_history.py \
  --entry-json data/raw/llm_history_exports/entry_example.json \
  --output results/summaries/entry_evaluation.json
```

Show script options:

```bash
python scripts/build_ssal.py --help
python scripts/evaluate_history.py --help
```

## Testing

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the core regression tests:

```bash
python -m pytest \
  tests/test_history_evaluation.py \
  tests/test_evaluate_history_script.py \
  tests/test_network_loader.py \
  tests/test_evaluation.py \
  tests/test_graph.py \
  -v
```

The tests cover:

- SSAL graph parsing and Dijkstra baseline behavior
- route-response JSON extraction and path validation
- route comparison metrics
- GeoPackage-to-SSAL network bundle loading
- offline history-entry and bulk-history evaluation helpers
- CLI argument parsing and output wiring

## Dashboard export requirements

Offline history evaluation expects exported dashboard route-history rows to include explicit top-level route metadata:

```json
{
  "origin": "25291564",
  "destination": "25291567"
}
```

The fallback field names are also supported:

```json
{
  "route_origin": "25291564",
  "route_destination": "25291567"
}
```

The evaluator intentionally does not parse origin/destination from prompt text. Rows without explicit route metadata are skipped with:

```json
{
  "status": "skipped",
  "reason": "missing_route_context"
}
```

## Current status

This repo reflects an evolving research workflow, not a finished software product.

Early experiment notes indicate:

- GPT-family models sometimes produced partially correct routes and distance estimates
- Gemini 2.5 Flash often failed to return the expected JSON format in earlier experiments
- performance worsened on more difficult routes
- output-format reliability was itself a major issue

The current evaluator is stricter than the early exploratory evaluator. It validates node paths against the SSAL-derived graph, recomputes candidate route length from graph edges, and compares the candidate route against Dijkstra ground truth.

Detailed chronology and test-by-test notes are kept in the supporting docs, summaries, and changelog rather than in the README.

## Evaluation note

The current route evaluator is SSAL-native. It validates LLM-produced node paths against the SSAL-derived graph, recomputes candidate route length from graph edges, and compares the candidate route against Dijkstra ground truth.

The default offline evaluator no longer requires:

```text
ORS_API_KEY
routingpy
OpenRouteService
```

## See also

- [CHANGELOG.md](CHANGELOG.md)
- [scripts/README.md](scripts/README.md)
- [results/summaries/](results/summaries/)
