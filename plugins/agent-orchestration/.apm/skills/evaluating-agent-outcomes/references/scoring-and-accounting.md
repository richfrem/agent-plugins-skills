# Scoring, accounting and usage measurement (generic, single implementation)

| Module | Responsibility | Caller supplies |
|---|---|---|
| `scoring.py` | Profile-driven scoring: validate ratings (no clamping), raw sum, `raw_fraction` or `weighted` headline, cost-adjusted ROI, optional bloat rule, deterministic event-log projection (`fold_assessment`, `rebuild_projection`) | A profile (dimensions, scale, weights, headline mode, bloat rule) |
| `accounting.py` | Model cost tiers and the historical substring lookup (default standard 1.0), usage-ledger fold (`fold_usage`, 30 recent), turn-budget check | Budget profiles (policy), ledger path |
| `usage_measure.py` | Zero-token vendor usage snapshots and diffs (claude `/usage`, agy JSON, codex rollouts), transcript token readers, secret scrubbing, catalog-priced `cost_usd` (None when a price is absent, never guessed) | Where to store snapshots, floors, policy |
| `outcome_eval.py` | Contract assessment; optional rubric scores come from `scoring.py` | Contract, evidence |

## Profiles
`assets/rubrics/pr-review.json` is an ordinary-work example (`weighted`: weights 3/2/1/1, headline `sum(w*v/max)/sum(w)`).
A project can bring its own: e.g. Sanctuary's five 0-3 dimensions use `fitness: raw_fraction` (headline `round(raw/15, 3)`) and a bloat rule
(model weight >= 3.0 with low token economy or outcome). The two profiles differ BY DESIGN: weights and the headline definition. The same
mechanism computes both (tests: `test_scoring_accounting.py`, fixture `tests/fixtures/sanctuary-contribution-v1.json`); a project's historical
scores stay valid because its profile reproduces its original arithmetic. Scores never alter `complete` or `integration_allowed`.

## What stays with the consumer
Budget policy (subscription profiles, soft limits), headroom floors and static ceilings, any predictor, attribution to its own work items,
storage locations and event names, dashboards and text output.
