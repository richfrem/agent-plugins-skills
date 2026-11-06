# Learning loop (repository-independent)

`scripts/work_loop.py` sequences one work item; it needs no Sanctuary schema.

1. **Contract** — goal, scope, observable acceptance and failure conditions, budget, authorization (`evaluating-agent-outcomes/references/work-contract.md`). `work_loop.py start` rejects an unusable contract.
2. **Retrieve** — `start` retrieves up to 3 relevant lessons BEFORE any dispatch (recorded in the trace).
3. **Delegate** — `work_loop.dispatch` goes through `cli-agent/scripts/run_agent.py` with ownership claim, cwd boundary, timeout and a structured result file.
4. **Evaluate** — `work_loop.evaluate` calls `outcome_eval.assess`. Worker exit is not completion.
5. **Repair** — `recommended=repair` returns the incomplete criteria to a worker; `escalate` at the attempt cap; `blocked` on budget.
6. **Integrate** — only when `complete` AND the caller's authorization allows (`integration_allowed`). Scores do not matter.
7. **Record** — `lessons.py add` (specific, evidenced), `eval_cli.py repair record` for recurring classes. No mission per lesson.
8. **Apply and measure** — `lessons.py use` records helped / no_effect / harmful on later work; `repair applied` counts opportunities.

Independent review and integration of ready deliveries proceed while other workers run.

## Ownership
| Capability | Owner |
|---|---|
| Outcome loop, sequencing, redispatch, trace | `orchestrating-agent-work` |
| Launch checks (claim, cwd, executable, timeout, clean context), structured result, usage capture | `cli-agent` (`run_agent.py`, `dispatch_guard.py`) |
| Findings, validity, costs, interventions, lessons | `evaluating-agent-outcomes` |
| Mission lifecycle, hypotheses, verdicts, governance | the consuming repository (e.g. Sanctuary) |

## Enforced by code vs instructed
Enforced in `run_agent.py` when the flags are passed: duplicate-unit refusal, cwd boundary, executable resolved on the worker PATH and version-probed, timeout (process-group kill on the streaming path), clean-context flags for claude, structured result JSON. NOT enforced (instructions the agent must follow): no git writes by workers, staying in scope, reviewing while workers run, honoring a standing authorization. A direct or manual `run_agent.py` call without the flags, or a direct CLI invocation, bypasses all of it. Clean context is requested, not probed: verify with `dispatch_guard.py context-check` on a stream-json probe. Ordinary repository work needs repository context; use `--clean-context` only for clean experimental conditions.
