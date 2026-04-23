# Changelog

All notable changes to this repository are documented here.

## 2026-04-23

### Added

- Added Southern Helsinki routing-network GeoPackage inputs under `data/raw/routing_networks/`
- Added stable SSAL export artifact under `data/derived/ssal/`
- Added dashboard history export JSONs under `data/raw/llm_history_exports/`
- Added `requirements.txt` for Python dependency installation
- Added `.env.example` for evaluator configuration
- Added `scripts/README.md` with setup, configuration, and usage instructions

### Changed

- Reorganized the repository around the routing-evaluation workflow
- Rewrote the root `README.md` to reflect the current project scope, workflow, and setup
- Moved reusable SSAL logic into `research/ssal.py`
- Cleaned up `research/ssal.py` to read more like shared library code
- Updated the route evaluator to use the cleaned repo layout
- Modularized `scripts/evaluate_history.py` with reusable functions, `main()`, and `if __name__ == "__main__":`
- Added CLI and environment-based configuration support to `scripts/evaluate_history.py`
- Added support for loading evaluator configuration from a repo-root `.env` file
- Improved evaluator reporting for malformed and cropped JSON outputs
- Added run-level summary reporting for evaluated and skipped entries
- Improved evaluator handling for mixed dashboard export history entries

### Archived

- Moved legacy prototype scripts under `archive/prototypes/`

### Cleaned

- Removed earlier filename churn from the cleaned branch history
- Removed notebook add/delete detours from the cleaned branch history
- Removed move-only and upload-style noise from the cleaned branch history
- Preserved original authorship where appropriate while rebuilding the cleaned history
- Removed `docs/project_overview.md` after splitting its role across `README.md`, `scripts/README.md`, `CHANGELOG.md`, and `results/summaries/`

## 2026-04-20

### Added

- Added routing experiment history exports for dashboard-based evaluation
- Added routing experiment notes and summaries
- Added/updated project overview documentation for the routing work

### Changed

- Expanded route-evaluation experimentation based on exported model outputs
- Continued comparison of GPT-family and Gemini-family outputs on SSAL routing tasks

## 2026-04-16

### Added

- Added earlier dashboard history exports for routing experiments
- Added initial routing experiment result notes

## 2026-04-13

### Added

- Added project overview notes describing the script inventory, SSAL logic, and evaluation direction

## 2026-04-12

### Added

- Added early route-evaluation prototype script
- Added direct-LLM routing prototype script
- Added initial SSAL conversion script
- Added Helsinki routing-network GeoPackage inputs

## Notes

- This changelog focuses on notable repository-level changes.
- Detailed experiment chronology, observations, and intermediate findings should remain in supporting documentation rather than in the changelog.
