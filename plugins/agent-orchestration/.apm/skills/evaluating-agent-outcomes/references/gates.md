# Gates before and after model evaluation

| Situation | Gate (`eval_cli.py`) |
|---|---|
| Evaluator untested before responses | `fixtures`: run it on synthetic cases first |
| Output contract unproven | `pilot` on development items; pilot ids must not be reused as confirmatory items |
| Finished benchmark: what may it claim? | `validity` (legacy; assumes a relative-reduction claim): adherence < 0.8 -> MECHANICS_ONLY; no/floor/ceiling baseline -> UNSCORABLE. Prefer `assess_claim` |
| Claim-specific validity | `eval_core.assess_claim` with claim `{type: relative_reduction / absolute_difference / gain / descriptive_rate / adherence, baseline, treatment}`: a relative reduction from a zero baseline is UNDEFINED (value withheld) while absolute difference, descriptive rates (a zero is informative) and adherence stay reportable; gain needs headroom; low adherence caps every behavioral claim at MECHANICS_ONLY; descriptive rates are always returned; historical records are not rescored |
| Choosing the check | `select`: deterministic first; never shrink a preregistered requirement (checkpoint instead) |
| Human effort | `intervention`: required_authorization, necessary_clarification, execution_failure_correction, scope_change; only the third is a correction; an observed event is required |
| Same failure twice | `repair record`; later opportunities via `repair applied`; `repair report` gives recurrence over applicable opportunities |
| Cost | `invest`: execution, orchestration_review, retry_failed, verification, repair; unknown stays unknown |
