# research

[![Regression Tests](https://github.com/spatial-ninjas/research/actions/workflows/regression-tests.yml/badge.svg)](https://github.com/spatial-ninjas/research/actions/workflows/regression-tests.yml)
[![PyPI](https://img.shields.io/pypi/v/spatial-ninjas-research?label=spatial-ninjas-research)](https://pypi.org/project/spatial-ninjas-research/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Reusable SSAL, graph, network-loading, and route-evaluation utilities for Spatial Ninjas.

Package version: **0.1.0**  
Python package: **`spatial-ninjas-research`**  
Import package: **`research`**

This repository contains the **research and evaluation side** of the LLM spatial-routing project. It provides the shared Python utilities used to convert routing-network data into SSAL, build an SSAL-derived graph, compute Dijkstra ground truth, and evaluate model-generated route responses.

The broader project compares GPT-family and Gemini-family models on route-generation tasks over an OpenStreetMap-derived Southern Helsinki network.

## Relationship to [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard)

The project is split across two repositories:

- [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard): run prompts, compare OpenAI and Gemini outputs, store/export history, and inspect route results visually
- [research](https://github.com/spatial-ninjas/research): provide reusable SSAL, graph, network-loading, route-evaluation, and offline history-evaluation utilities

For deployment, the dashboard should depend on the published `spatial-ninjas-research` package instead of requiring a sibling checkout of this repository. For local development, the dashboard can still install this repository as an editable package.

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

## Route evaluation data

Cleaned route-evaluation data and grouped summaries are available under:

- [`data/route-evaluation/`](data/route-evaluation/)

This folder contains the selected route cases used in the final LLM route-finding analysis. The public-facing data is derived from dashboard route-evaluation history, but it is not a full database export. Obsolete experiments, unrelated test runs, provider-specific raw API responses, full model responses, large route arrays, SSAL hashes, and other internal metadata are intentionally omitted.

The folder contains:

- `README.md` — notes for the cleaned route-evaluation dataset
- `relevant_route_history_cleaned.json` — cleaned per-run evaluation data for the selected route cases
- `route_case_config_evaluation_summary.csv` — tabular summary grouped by route case, provider/model configuration, prompt template, and SSAL profile
- `route_case_config_evaluation_summary.md` — human-readable version of the grouped summary for GitHub browsing

The `indices_base0_ranges` field in the summaries uses base-0 indexing and refers to positions in `relevant_route_history_cleaned.json`.

## Installation

### Install the released package

Install the released package with:

```bash
python -m pip install spatial-ninjas-research==0.1.0
```

The PyPI distribution name is `spatial-ninjas-research`, while the Python import path remains `research`:

```python
from research.ssal import gpkg_to_ssal
from research.graph import dijkstra_shortest_path
from research.evaluation import evaluate_route_response
from research.network_loader import load_network_bundle_from_gpkg
```

Verify the installed package with:

```bash
python - <<'PY'
import research
from research.ssal import gpkg_to_ssal
from research.history_evaluation import evaluate_entry_file

print(research.__version__)
print('research package ok')
PY
```

The Python package contains reusable code. Large routing data files, such as GeoPackage inputs, are not distributed through PyPI. For dashboard deployment, the canonical GeoPackage should be provided separately through local configuration or remote object storage.

### Develop this repository locally

Create and activate a virtual environment first.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Runtime dependencies are declared in `pyproject.toml`. The pinned `requirements.txt` is generated from `pyproject.toml` with `pip-compile` and can be used when a locked dependency set is preferred:

```bash
python -m pip install -r requirements.txt
```

Development dependencies are exposed through the `dev` extra and mirrored by `requirements-dev.txt`:

```bash
python -m pip install -r requirements-dev.txt
```

### Local editable install from the dashboard repo

The dashboard can use the published package for deployment, but local editable development is still useful when changing the research utilities and dashboard together.

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

This editable install should be treated as a development override. Deployment should use the versioned package from PyPI.

### Environment configuration

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

Stable generated SSAL text artifacts may be versioned in this repo for reproducible experiments, but large GeoPackage inputs are not part of the Python package.

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

### Archived notes and earlier experiments

Earlier exploratory notes, route-test notes, and enhancement-strategy examples are kept under:

- [archive/](archive/)

These files are historical references and are not treated as the main current workflow.

### Comparison interface and history

The project also uses a comparison interface in the separate dashboard repo for side-by-side model testing and persisted history. That history is later exported and analyzed here.

## Repository layout

- `research/` — reusable Python logic for SSAL conversion, graph utilities, network loading, route evaluation, and history-evaluation adapters
- `scripts/` — executable SSAL generation, SSAL equivalence checking, and history-evaluation scripts
- `tests/` — regression tests for graph, evaluation, network loading, history helpers, and CLI wiring
- `data/raw/routing_networks/` — OSM-derived GeoPackage inputs used as routing-network sources
- `data/derived/ssal/` — stable generated SSAL text artifacts
- `data/route-evaluation/` — cleaned public route-evaluation data and grouped summaries
- `archive/` — older route-evaluation notes, route-test notes, and enhancement-strategy examples

## Common commands

Build the default SSAL artifact:

```bash
python scripts/build_ssal.py
```

Evaluate a dashboard history export:

```bash
python scripts/evaluate_history.py \
  --history-json path/to/dashboard_history_export.json \
  --output build/history_evaluation.json
```

Evaluate one exported history row:

```bash
python scripts/evaluate_history.py \
  --entry-json path/to/entry_example.json \
  --output build/entry_evaluation.json
```

Show script options:

```bash
python scripts/build_ssal.py --help
python scripts/check_ssal_equivalence.py --help
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

Detailed chronology and test-by-test notes are kept in `archive/`, `data/route-evaluation/`, and the changelog rather than in the README.

## Evaluation note

The current route evaluator is SSAL-native. It validates LLM-produced node paths against the SSAL-derived graph, recomputes candidate route length from graph edges, and compares the candidate route against Dijkstra ground truth.

## See also

- [CHANGELOG.md](CHANGELOG.md)
- [scripts/README.md](scripts/README.md)
- [data/route-evaluation/README.md](data/route-evaluation/README.md)
