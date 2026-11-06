# Work contract, findings and records (v1)

Contract (JSON; caller-defined `id`/`type`, no mission schema needed):

```json
{"id": "t1", "type": "task|issue|pr|experiment|...", "goal": "...",
 "scope": {"paths": ["files or dirs that may change"]},
 "acceptance": [{"id": "A1", "text": "...", "required": true,
                 "check": {"kind": "command|file_exists|file_contains|manual", "argv": ["..."], "expect_exit": 0, "expect_stdout_contains": ["..."]}}],
 "failure_conditions": [{"id": "F1", "text": "...", "check": {"kind": "file_exists", "path": "ERROR.txt"}}],
 "budget": {"max_attempts": 3, "max_tokens": 50000, "per_attempt_token_reserve": 8000},
 "authorization": {"may_merge": false},
 "rubric": {"id": "optional", "dimensions": {"correctness": {"max": 3, "weight": 3}}}}
```

Checks run with cwd confined to the root. A passing failure-condition check means the failure occurred. A `manual` criterion is `unverified` until `evidence.manual_confirmations[id]` cites a reference.

Findings (`outcome_eval.assess`): `criteria[]` (result pass|fail|unverified, detail, evidence_ref), `failure_hits`, `incomplete`, `blockers`, `limitations`, `usage` (tokens or null), `complete`, optional `scores` (rubric id, normalized value, problems), `integration_allowed` (requires complete AND the caller's authorization; scores irrelevant), `recommended` (accept | repair | blocked | escalate | fix_contract), `repair_instructions`.

Records (`eval_core`, JSONL, `v:1`, `kind`): `lesson`, `lesson_use`, `intervention`, `repair`, `repair_application`. Legacy `event_type` lines are still read. Store must resolve inside the declared root. Nested workers: attribute tokens once, to the worker's own unit. API-equivalent price is never mixed with subscription token usage.

Lesson fields: trigger, failure, evidence, cause (known|suspected), action, verification, limits, tags. `find` returns up to 3 compact matches. A lesson earns no credit until `lesson_use` records an outcome (helped|no_effect|harmful).

## Budget (validated by `accounting.validate_budget`; per work item)
`max_attempts` required positive integer (booleans, floats, strings, zero, negatives rejected); `max_tokens` and `per_attempt_token_reserve` optional positive
integers (reserve <= ceiling, needs a ceiling); unknown keys rejected. `accounting.summarize_attempts` folds an append-only attempt ledger (last record per
attempt id wins; each backend attempt counted once; unknown usage stays unknown; running attempts count as unknown) and `accounting.admit` decides whether one
more execution attempt may launch. Preflight refusals and evaluation calls are tracked separately from execution attempts. Totals are lower bounds whenever
anything is unknown. Token limits are admission control: no backend guarantees a hard cap.
