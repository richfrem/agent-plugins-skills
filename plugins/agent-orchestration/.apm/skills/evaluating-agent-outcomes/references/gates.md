# Gates before and after model evaluation

| Situation | Gate (`eval_cli.py`) |
|---|---|
| Evaluator untested before responses | `fixtures`: run it on synthetic cases first |
| Output contract unproven | `pilot` on development items; pilot ids must not be reused as confirmatory items |
| Finished benchmark: what may it claim? | `validity`: adherence < 0.8 -> MECHANICS_ONLY; no/floor/ceiling baseline -> UNSCORABLE; malformed answers stay in the denominator |
| Choosing the check | `select`: deterministic first; never shrink a preregistered requirement (checkpoint instead) |
| Human effort | `intervention`: required_authorization, necessary_clarification, execution_failure_correction, scope_change; only the third is a correction; an observed event is required |
| Same failure twice | `repair record`; later opportunities via `repair applied`; `repair report` gives recurrence over applicable opportunities |
| Cost | `invest`: execution, orchestration_review, retry_failed, verification, repair; unknown stays unknown |
