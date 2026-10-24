# Lab Loop (the `loop` mode)

The single loop that improves a target skill or agent in the lab. It owns orientation, mutation and
close. It never scores: each change goes to the `score` mode.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> The only improvement loop in the skill lab: orient from the improvement ledger, evals/results.tsv, references/program.md and open map debt, mutate one thing, call the `score` mode for every change (KEEP or DISCARD), then close with surveys, ledger update, metrics and memory promotion through the `memory` mode. Runs solo or as ORCHESTRATOR with INNER_AGENT and PEER_AGENT sessions sharing the kernel event bus. Use when the user says "run the improvement loop", "run the autoresearch loop on", "optimize this skill for N iterations", "run an improvement cycle", "continuous improvement loop with KEEP or DISCARD", "ORCHESTRATOR and PEER_AGENT", or "close the loop". DO NOT USE for a single KEEP/DISCARD check or one RED-GREEN-REFACTOR patch (the `score` mode), building the lab repo (the `setup` mode), planning (the `plan` mode), reviewing and porting results (the `backport` mode), run logs and charts (the `log` mode), or session memory alone (the `memory` mode).

## Contents

- [Critical constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical constraints

1. **Every change is scored**: call the `score` mode for each mutation; no manual rollback and no self-assessed KEEP.
2. **Locked evaluator**: only the target `SKILL.md` (and, as a second-order move, the proposer prompt or the target skill's `program.md`) is mutated; never `evaluate.py` or `evals/evals.json`.
3. **One variable per iteration**, and a documented hypothesis before the first mutation.
4. **Session close is mandatory**: surveys, ledger, metrics, registry and memory run even when the target score is not reached.
5. **Budget guard**: 10 iterations per session, 3 consecutive DISCARDs trigger a strategy review (see lab-limits).
6. **Do not skip orientation**: no agent starts cold.

## Quick start

From a lab prepared by the `setup` mode, with a baseline already recorded in `<path/to/target-skill>/evals/results.tsv`:

```text
Run the improvement loop on <path/to/target-skill> for 5 iterations.
```

Each iteration: classify the failure, propose one change, invoke the `score` mode on `<path/to/target-skill>`, act on KEEP or DISCARD. If no baseline exists, have the `score` mode record it first.

## Workflow

1. **Orient (Stage 0)**: read `context/memory/improvement-ledger.md`, the target's `evals/results.tsv`, the target skill's `program.md`, the test registry, `context/memory.md`, recent surveys, the last 100 lines of `context/events.jsonl`, and open map debt (`Repeat: YES` first). Write the hypothesis and register the cycle. See [stage-0-orientation.md](../stage-0-orientation.md).
2. **Mutate (Stage 1)**: classify the failure, propose one change, log friction events as they occur. See [mutation-protocol.md](../mutation-protocol.md) and [stage-1-execution.md](../stage-1-execution.md).
3. **Score (Stage 2)**: invoke the `score` mode. With a PEER_AGENT, the peer scores independently from its own session. See [stage-2-verification.md](../stage-2-verification.md).
4. **Decide (Stage 3)**: KEEP is applied and committed; DISCARD writes a correction packet and re-signals the inner agent. See [stage-3-decision.md](../stage-3-decision.md).
5. **Repeat** from step 2 until the cap, the target score or the budget guard.
6. **Close (Stage 4)**: friction gate, surveys, post-run metrics, session log, loop report, test registry, improvement ledger, then the `memory` mode for L3 promotion, auto-memory, Triple-Loop trigger check and lock release. See [stage-4-close.md](../stage-4-close.md).

When the lab run is complete, hand the diff to the `backport` mode and the run record to the `log` mode.

## Verification

The Stop hook runs `post_run_metrics.py` at turn end (it ships with the plugin's hooks, not with this skill). Confirm a `metric` event was emitted, `friction` and `friction.resolved` counts match, and the ledger has a new row.

## References

- [mutation-protocol.md](../mutation-protocol.md) - one iteration, proposer calls, second-order mutations.
- [stage-0-orientation.md](../stage-0-orientation.md) - pre-flight reads and test registration.
- [stage-1-execution.md](../stage-1-execution.md) - inner agent duties.
- [stage-2-verification.md](../stage-2-verification.md) - independent scoring.
- [stage-3-decision.md](../stage-3-decision.md) - KEEP and DISCARD handling.
- [stage-4-close.md](../stage-4-close.md) - mandatory close checklist.
- [lab-limits.md](../lab-limits.md) - budget guard, architecture, examples.
- [program.md](../program-example.md) - example optimization program.
- [orchestrator-meta-survey.md](../orchestrator-meta-survey.md) - multi-session retrospective.
- [cheapest_models.md](../cheapest_models.md) - proposer model costs.
- [improvement-ledger-spec.md](../improvement-ledger-spec.md), [post_run_survey.md](../post_run_survey.md), [metrics.md](../loop-metrics.md), [test-registry-protocol.md](../test-registry-protocol.md).
