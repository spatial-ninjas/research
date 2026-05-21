# Route evaluation dataset

This folder contains the cleaned route-evaluation results used for the LLM geospatial route-finding analysis.

The data is derived from saved dashboard route-evaluation history. Obsolete experiments and unrelated test runs have been filtered out, leaving only the selected route cases used in the final analysis.

## Files

- `relevant_route_history_cleaned.json`  
  Cleaned per-run evaluation data. Provider-specific raw API responses, full model responses, large route arrays, SSAL hashes, and internal metadata have been removed.

- `route_case_config_evaluation_summary.csv`  
  Tabular summary grouped by route case, model/API configuration, prompt template, and SSAL profile.

- `route_case_config_evaluation_summary.md`  
  Human-readable version of the same summary for GitHub browsing.

## Route cases

The selected route cases are grouped into five categories:

1. Direct route
2. Long multi-hop route
3. Junction-heavy route
4. Near shortest alternatives
5. Shortest alternative is a one-way street

The `case` field identifies the specific route case. The `indices_base0_ranges` field uses base-0 indexing and refers to positions in `relevant_route_history_cleaned.json`.

## Notes

This is not a full database export. It is a public-facing cleaned dataset intended to support reproducibility and result inspection.
