# Route Evaluation Summary — 2026-04-20

This summary records the current output of `scripts/evaluate_history.py` on the routing history export for 2026-04-20.

## Run summary

- Total history entries: 30
- Routing-related entries: 28
- Successfully evaluated: 10
- Skipped (`cropped_json`): 12
- Skipped (`missing_path`): 5
- Skipped (`non_routing_entry`): 2
- Skipped (`provider_error`): 1

## Per-model summary

| Model | Total seen | Evaluated | Skipped | Avg node accuracy | Avg distance precision |
|---|---:|---:|---:|---:|---:|
| Gemini / gemini-2.5-flash | 15 | 2 | 13 | 18.3% | 18.3% |
| OpenAI / gpt-5.4 | 12 | 6 | 6 | 29.1% | 34.0% |
| OpenAI / gpt-5.4-mini | 3 | 2 | 1 | 41.2% | 51.7% |

## Notable observations

- A large share of Gemini entries were skipped because the response was cropped or otherwise incomplete.
- OpenAI models were evaluated more often successfully in this run.
- Shorter and simpler routes performed much better than harder routes.
- The route from `25291537` to `313984198` produced the strongest result in this run, with 66.7% node-sequence accuracy and 99.1% distance precision.

## Example evaluated cases

### Model ID 11 — OpenAI / gpt-5.4
- Route: `25291537 -> 313984198`
- Finish status: `completed`
- Max output tokens: `512`
- Node Sequence Accuracy: `66.7%`
- Distance Precision: `99.1%`
- Length Comparison: `LLM 11.1m | Algorithm 11.0m`

### Model ID 30 — Gemini / gemini-2.5-flash
- Route: `25291537 -> 25291550`
- Finish status: `STOP`
- Max output tokens: `1600`
- Node Sequence Accuracy: `11.5%`
- Distance Precision: `26.4%`
- Length Comparison: `LLM 69.1m | Algorithm 262.0m`

## Evaluation note

The current node-sequence comparison is an approximate exploratory metric based on OpenRouteService route geometry. It is useful for rough comparison, but it is not yet a fully graph-native path-equivalence metric.
