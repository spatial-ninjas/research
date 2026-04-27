# Changelog

All notable changes to this repository are documented here.

## 2026-04-27 — Network loader and offline history evaluator refactor

### Network loader

- Added `research.network_loader` as the reproducible network-loading layer.
- Added `sha256_text()` for stable SSAL text fingerprints.
- Added `sha256_file()` for local file checksum verification.
- Added frozen `NetworkBundle` containing:
  - GeoPackage path
  - generated SSAL text
  - SSAL hash
  - SSAL-derived graph
  - edge layer name
  - node layer name
- Added `load_network_bundle_from_gpkg()`.
- Ensured the graph used for evaluation is built from generated SSAL text, not directly from the GeoPackage.
- Added default SSAL generation attributes for routing and debugging:
  - `length`
  - `name`
  - `oneway`
  - `from_x`
  - `from_y`
  - `to_x`
  - `to_y`
- Added optional cached-file loading through `fetch_or_reuse_cached_file()`.
- Added cache reuse, missing-file download, checksum verification, mismatch refetching, and invalid-download cleanup behavior.
- Added an optional real GeoPackage integration test that skips cleanly when the data artifact is unavailable.

### Offline history evaluation

- Refactored offline route-history evaluation around the shared SSAL-native evaluator.
- Treated one dashboard route-history row as the primary evaluation unit.
- Added `load_entry()` for one-entry JSON files.
- Added `load_history()` for bulk dashboard history exports.
- Added response-text extraction from known export fields:
  - `response_text`
  - `response`
  - `text`
- Added history metadata preservation:
  - raw `id` normalized to `entry_id`
  - `entry_id` fallback
  - `provider`
  - `model`
  - `finish_status`
  - `max_output_tokens`
- Added route-context extraction from explicit metadata:
  - `origin`
  - `destination`
  - `route_origin`
  - `route_destination`
- Entries without explicit route context are skipped with structured reason `missing_route_context`.
- Added `evaluate_route_history_entry()` as the single-entry adapter around `evaluate_route_response()`.
- Added `evaluate_entry_file()` for one-entry JSON input.
- Added `evaluate_history_file()` for bulk history JSON input.
- Bulk evaluation loads the `NetworkBundle` once and reuses it for every row.
- Bulk evaluation loops over the same single-entry evaluator rather than adding separate evaluation logic.
- Results include `ssal_hash` so the evaluated network representation is traceable.

### Bulk summaries and JSON output

- Added bulk result summary generation.
- Added overall aggregate metrics:
  - `total_entries`
  - `evaluated_entries`
  - `skipped_entries`
  - `skip_reasons`
  - `valid_path_rate`
  - `average_relative_length_error`
  - `average_declared_length_relative_error`
- Added grouped provider/model summaries under `per_model`.
- Added grouped origin/destination summaries under `per_route`.
- Missing provider/model values are grouped as `unknown/unknown`.
- Missing origin/destination values are grouped as `unknown->unknown`.
- Missing skip reasons are grouped as `unknown`.
- Summary generation is pure aggregation over already-produced evaluation rows. It does not re-parse model responses, rebuild graphs, call Dijkstra, or call the evaluator again.
- Added JSON output formatting for one-entry and bulk results.
- One-entry outputs are wrapped under `result`.
- Bulk outputs contain both `summary` and row-level `results`.
- Added JSON writing with automatic parent directory creation.
- Added validation for missing, mixed, or incomplete output payloads.

### CLI workflow

- Added argument parsing for `scripts/evaluate_history.py`.
- Added mutually exclusive input modes:
  - `--entry-json`
  - `--history-json`
- Added network configuration arguments:
  - `--gpkg-path`
  - `--edges-layer`
  - `--nodes-layer`
- Added optional output argument:
  - `--output`
- Added built-in defaults for the Southern Helsinki slimmed/cropped network.
- Added environment variable overrides:
  - `GPKG_PATH`
  - `EDGES_LAYER`
  - `NODES_LAYER`
- Added `main()` wiring for one-entry and bulk modes.
- CLI writes JSON to `--output` when provided.
- CLI prints JSON to stdout when `--output` is omitted.
- Added direct script execution support so `python scripts/evaluate_history.py --help` works from the repository root.

### Extraction and module boundaries

- Extracted reusable offline history-evaluation helpers into `research.history_evaluation`.
- Kept `scripts.evaluate_history` as a thin CLI wrapper.
- Final split:
  - `research.graph` — SSAL graph model and Dijkstra baseline
  - `research.evaluation` — shared route-response evaluator
  - `research.network_loader` — GeoPackage → SSAL → graph bundle loading
  - `research.history_evaluation` — dashboard/export row adaptation, summaries, JSON output helpers
  - `scripts.evaluate_history` — CLI defaults, argument parsing, and `main()`
- Split tests accordingly:
  - `tests/test_history_evaluation.py` covers reusable helper behavior
  - `tests/test_evaluate_history_script.py` covers CLI behavior
- Updated root README and `scripts/README.md` to describe the post-extraction architecture.

### ORS/routingpy removal from default path

- Removed ORS/routingpy from the default offline evaluation path.
- Removed `routingpy` from `requirements.txt`.
- Removed `ORS_API_KEY` from `.env.example`.
- Replaced old OpenRouteService baseline wording with Dijkstra ground truth over the SSAL-derived graph.
- Confirmed remaining ORS/routingpy mentions only document that they are no longer required or test that `ORS_API_KEY` is not required.
- Closed #63 from the offline history-evaluation side.

### Testing and validation

- Added and updated tests for:
  - network loading
  - cache handling
  - one-entry history evaluation
  - bulk history evaluation
  - summary aggregation
  - JSON output formatting/writing
  - CLI argument parsing and wiring
- Final focused validation:
  - `tests/test_history_evaluation.py`: 39 passed
  - `tests/test_evaluate_history_script.py`: 12 passed
- Final related regression group:
  - 230 tests passed across graph, evaluator, network loader, history helpers, and CLI wiring.
- Verified direct CLI help:
  - `python scripts/evaluate_history.py --help`
- Verified manual one-entry and bulk CLI runs.
- Manual validation confirmed that exported dashboard rows need top-level `origin` and `destination` fields for offline evaluation.

### Follow-up notes

- The dashboard export flow should include top-level `origin` and `destination` fields in route-history exports.
- The fallback field names `route_origin` and `route_destination` are supported.
- The evaluator intentionally avoids parsing origin/destination from prompt text to keep offline evaluation deterministic and avoid duplicating prompt-parsing logic.

---

## 2026-04-26 — SSAL graph model and shared route evaluator

### SSAL graph model

- Added `research.graph` as the SSAL-native graph layer.
- Added immutable `Edge` objects.
- Added directed `Graph` objects with string node IDs.
- Added SSAL parsing into directed graph structures.
- Preserved target-only nodes when parsing SSAL.
- Preserved edge metadata from SSAL attributes.
- Added graph helpers:
  - `nodes()`
  - `has_node()`
  - `get_edge()`
  - `has_edge()`
  - `path_length()`
- Added support for numeric-looking node IDs while keeping them as strings.
- Added explicit validation for malformed SSAL lines and missing/invalid edge lengths.
- Added tests for directed-edge behavior, reverse-edge non-inference, target-only nodes, metadata preservation, path-length calculation, and parser edge cases.

### Dijkstra baseline

- Added deterministic Dijkstra shortest-path search over the SSAL-derived graph.
- Used the SSAL graph itself as the ground-truth baseline instead of an external routing service.
- Added handling for:
  - unknown origin nodes
  - unknown destination nodes
  - disconnected graph components
  - no-path cases
  - origin equals destination
  - target-only destination nodes
  - negative edge-length rejection when reachable
  - unreachable negative edges that should not affect the searched path
- Added deterministic tie-breaking for equal-distance frontier nodes using lexicographic node ID ordering.
- Added integration tests against the real versioned SSAL artifact when available.
- Added known-node and known-shortest-path tests for the real SSAL artifact.
- Documented SSAL graph utilities, directed-edge handling, parser assumptions, target-only nodes, and deterministic Dijkstra tie-breaking.

### Shared route-response evaluator

- Added `research.evaluation` as the shared evaluator used by offline workflows and future dashboard integration.
- Added `clean_json()` for recovering JSON route objects from model responses.
- Supported plain JSON, fenced JSON blocks, generic Markdown fences, irregular fence lengths, surrounding text, and invalid extracted JSON for later decode handling.
- Added `extract_path()` for candidate route path extraction.
- Used `route[*].node` as the primary expected model-output schema.
- Kept `edge_name` out of path-validity logic.
- Preserved route entries with `edge_name` for display/debugging.
- Added compatibility handling for older/manual fallback path formats.
- Added `extract_declared_length()` for model-declared `total_length`.
- Added handling for numeric, string, missing, null, non-numeric, zero, and negative declared lengths.
- Added candidate path validation against the directed SSAL-derived graph.
- Candidate path validation now reports:
  - empty path
  - wrong origin
  - wrong destination
  - unknown nodes
  - missing directed edges
  - computed candidate length when valid
- Added route comparison metrics:
  - exact path match
  - node overlap
  - directed edge overlap
  - candidate length vs Dijkstra ground-truth length
  - absolute length error
  - relative length error
- Added declared-length comparison metrics:
  - declared vs graph-computed candidate length
  - declared absolute error
  - declared relative error
- Added `evaluate_route_response()` as the top-level shared evaluator.
- Added behavior for invalid JSON, missing JSON, non-object JSON, invalid candidate paths, unknown nodes, missing edges, and ground-truth failures.
- Ensured invalid candidate paths can still be compared against ground truth when possible.
- Added extensive unit tests for JSON extraction, route extraction, validation, comparison metrics, declared-length metrics, and full evaluator behavior.
- Closed #60 and #61 through graph documentation and complete route-response evaluation.

---

## 2026-04-23 — Repository cleanup, SSAL workflow, and early evaluator structure

### Repository cleanup

- Reorganized the research repository around the current routing-evaluation workflow.
- Updated the root README to describe the role of this repository as the research/evaluation side of the project.
- Clarified the relationship between this repository and `llm-compare-dashboard`.
- Added and updated script documentation in `scripts/README.md`.
- Removed older project-overview documentation once the README and changelog became the canonical project documentation.
- Added local editable-install instructions so the dashboard repository can import the research package during development.
- Added package metadata in `pyproject.toml` for editable installs.
- Added `.gitignore` rules to reduce repository clutter.
- Added `CHANGELOG.md`.
- Added route-evaluation summary notes under `results/summaries/`.
- Moved legacy prototype scripts under `archive/prototypes/`.
- Completed a filename-normalization pass across active workflow areas.

### Routing-network data and history exports

- Preserved GeoPackage inputs for the Southern Helsinki routing network.
- Added the slimmed/cropped GeoPackage as the main local routing-network source.
- Added stable SSAL export artifact for the Southern Helsinki network.
- Added dashboard history exports for routing experiments.

### SSAL conversion and artifacts

- Added the initial SSAL conversion foundation in `research.ssal`.
- Improved SSAL conversion features.
- Refined the SSAL conversion module structure.
- Added `scripts/build_ssal.py` as the documented CLI entry point for regenerating the SSAL artifact.
- Added `scripts/check_ssal_equivalence.py` for comparing SSAL outputs after cleanup.
- Made SSAL equivalence checking reusable by removing hardcoded file names and supporting configurable inputs.
- Updated SSAL build defaults to match the currently versioned artifact configuration.
- Documented the SSAL generation workflow and its relationship to the versioned SSAL artifact.
- Verified that the regenerated SSAL representation preserved the same graph structure, with differences limited to ordering and street-name normalization.

### Early route evaluation

- Added early route-evaluation and direct-LLM prototypes.
- Modularized the first route evaluator script.
- Added initial `.env.example`, `requirements.txt`, and script documentation for offline evaluation.
- Added CLI and environment-based configuration support to the early evaluator.
- Added support for loading evaluator configuration from a repo-root `.env` file.
- Improved evaluator reporting for malformed and cropped JSON outputs.
- Added run-level summary reporting for evaluated and skipped entries.
- Improved evaluator handling for mixed dashboard export history entries.
- The early evaluator still used an exploratory ORS/routingpy baseline at this stage, later replaced by the SSAL-native evaluator on 2026-04-26 and 2026-04-27.

### Documentation

- Rewrote README around the routing-evaluation workflow.
- Added project workflow documentation for:
  - raw routing-network inputs
  - SSAL artifacts
  - script entry points
  - local setup
  - dashboard/research repo relationship
- Updated `CHANGELOG.md` to cover SSAL build flow, reusable script entry points, and cleanup milestones.

---

## Earlier routing experiment notes

### Added

- Added early dashboard history exports for routing experiments.
- Added initial routing experiment notes and summaries.
- Added project overview notes describing the script inventory, SSAL logic, and evaluation direction.
- Added early route-evaluation prototype scripts.
- Added direct-LLM routing prototype scripts.
- Added the initial SSAL conversion script.
- Added Helsinki routing-network GeoPackage inputs.

### Changed

- Expanded route-evaluation experimentation based on exported model outputs.
- Continued comparison of GPT-family and Gemini-family outputs on SSAL routing tasks.
