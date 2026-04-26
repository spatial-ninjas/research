# research

Research workspace for evaluating LLM routing behavior on a simplified street-network representation of Southern Helsinki.

This repository contains the **research and evaluation side** of the project: routing-network inputs, stable SSAL artifacts, exported experiment inputs, and analysis scripts. The broader project compares GPT-family and Gemini-family models on routing tasks over an OpenStreetMap-derived Helsinki network, using [Routingpy](https://routingpy.readthedocs.io/en/latest/) as the reference baseline.

## Relationship to [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard)

The project is split across two repositories:

- [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard): run prompts, compare OpenAI and Gemini outputs side by side, and store/export history
- [research](https://github.com/spatial-ninjas/research): prepare routing artifacts, version experiment inputs, and evaluate routing results

The dashboard can use this repository as a local editable Python package during development. This allows the dashboard to import reusable logic from `research` without copying code between repositories.

## Project scope

The project studies how LLMs handle route-generation tasks when given a compact graph-like representation of a real street network instead of a standard map UI. The current reference map is a selected area of Southern Helsinki derived from OpenStreetMap. The current evaluation focuses on GPT and Gemini models.

Main evaluation concerns:

- structured output correctness
- plausible node sequence selection
- distance estimation quality
- robustness as route difficulty increases

## Current workflow

1. Prepare an OSM-derived routing network
2. Build the SSAL artifact from the GeoPackage input
3. Run routing prompts in [llm-compare-dashboard](https://github.com/spatial-ninjas/llm-compare-dashboard)
4. Export the dashboard history as JSON
5. Store the export in this repository
6. Evaluate the results with the scripts here
7. Record summaries and notes for later review

## Setup

Create and activate a virtual environment first.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
````

### Local editable install

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

Verify the import with:

```bash
python -c "from research.ssal import gpkg_to_ssal; print('ok')"
```

The package name is `spatial-ninjas-research`, while the Python import path remains:

```python
from research.ssal import gpkg_to_ssal
```

Create a repo-root `.env` file:

```dotenv
ORS_API_KEY=your_ors_api_key_here
GPKG_PATH=data/raw/routing_networks/osm_southern_helsinki_slimmed_cropped.gpkg
HISTORY_JSON=data/raw/llm_history_exports/llm_compare_history_2026-04-20.json
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

### Evaluation scripts

The current script workflow lives under:

- [scripts/](scripts/)

In particular:

- [scripts/build_ssal.py](scripts/build_ssal.py) builds the compact SSAL text artifact from the GeoPackage road-network input
- [scripts/evaluate_history.py](scripts/evaluate_history.py) evaluates exported dashboard history against the routing network and prints per-entry and summary results
- [scripts/README.md](scripts/README.md) documents dependencies, configuration, and usage

### LLM routing prototype

An earlier prototype script feeds SSAL data and a routing prompt to an LLM and expects a route in JSON format. It is kept for historical reference and is not treated as the main current workflow.

Current location:
- [archive/prototypes/](archive/prototypes/)

### Comparison interface and history

The project also uses a comparison interface (`app.py` in the separate dashboard repo) for side-by-side model testing and persisted history. That history is later exported and analyzed here.

## Repository layout

- `data/raw/routing_networks/` — OSM-derived GeoPackage inputs
- `data/derived/ssal/` — stable generated SSAL text artifacts
- `data/raw/llm_history_exports/` — exported dashboard history JSONs
- `research/` — reusable Python logic
- `scripts/` — executable SSAL generation and evaluation scripts
- `results/summaries/` — experiment notes and summaries
- `archive/prototypes/` — older prototype scripts

## Common commands

Build the default SSAL artifact:

```bash
python scripts/build_ssal.py
```

Evaluate the default exported history:

```bash
python scripts/evaluate_history.py
```

Show script options:

```bash
python scripts/build_ssal.py --help
python scripts/evaluate_history.py --help
```

## Current status

This repo reflects an evolving research workflow, not a finished software product.

Early experiment notes indicate:

- GPT-family models sometimes produced partially correct routes and distance estimates
- Gemini 2.5 Flash often failed to return the expected JSON format
- performance worsened on more difficult routes
- output-format reliability was itself a major issue

Detailed chronology and test-by-test notes are kept in the supporting docs, summaries, and changelog rather than in the README.

## Evaluation note

The current route evaluator uses an approximate exploratory node-sequence comparison between LLM-produced node paths and OpenRouteService route geometry. This is useful for rough comparison, but it is not yet a fully graph-native path-equivalence metric.

## See also

- [CHANGELOG.md](CHANGELOG.md)
- [scripts/README.md](scripts/README.md)
- [results/summaries/](results/summaries/)
