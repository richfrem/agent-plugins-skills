---
name: os-lab-loop
description: >
  The only improvement loop in the skill lab: orient from the improvement ledger, evals/results.tsv,
  references/program.md and open map debt, mutate one thing, call os-lab-scorer for every change
  (KEEP or DISCARD), then close with surveys, ledger update, metrics and memory promotion through
  os-memory-manager. Runs solo or as ORCHESTRATOR with INNER_AGENT and PEER_AGENT sessions sharing
  the kernel event bus. Use when the user says "run the improvement loop", "run the autoresearch
  loop on", "optimize this skill for N iterations", "run an improvement cycle", "continuous
  improvement loop with KEEP or DISCARD", "ORCHESTRATOR and PEER_AGENT", or "close the loop".
  DO NOT USE for a single KEEP/DISCARD check or one RED-GREEN-REFACTOR patch (os-lab-scorer),
  building the lab repo (os-lab-setup), planning (os-lab-planner), reviewing and porting results
  (os-lab-backport), run logs and charts (os-lab-log), or session memory alone (os-memory-manager).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Lab Loop (`os-lab-loop`)

The single loop that improves a target skill or agent in the lab. It owns orientation, mutation and
close. It never scores: each change goes to `os-lab-scorer`.

## Contents

- [Critical constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical constraints

1. **Every change is scored**: call `os-lab-scorer` for each mutation; no manual rollback and no self-assessed KEEP.
2. **Locked evaluator**: only the target `SKILL.md` (and, as a second-order move, the proposer prompt or `references/program.md`) is mutated; never `evaluate.py` or `evals/evals.json`.
3. **One variable per iteration**, and a documented hypothesis before the first mutation.
4. **Session close is mandatory**: surveys, ledger, metrics, registry and memory run even when the target score is not reached.
5. **Budget guard**: 10 iterations per session, 3 consecutive DISCARDs trigger a strategy review (see lab-limits).
6. **Do not skip orientation**: no agent starts cold.

## Quick start

From a lab prepared by `os-lab-setup`, with a baseline already recorded in `<path/to/target-skill>/evals/results.tsv`:

```text
Run the improvement loop on <path/to/target-skill> for 5 iterations.
```

Each iteration: classify the failure, propose one change, invoke `os-lab-scorer` on `<path/to/target-skill>`, act on KEEP or DISCARD. If no baseline exists, have `os-lab-scorer` record it first.

## Workflow

1. **Orient (Stage 0)**: read `context/memory/improvement-ledger.md`, the target's `evals/results.tsv`, `references/program.md`, the test registry, `context/memory.md`, recent surveys, the last 100 lines of `context/events.jsonl`, and open map debt (`Repeat: YES` first). Write the hypothesis and register the cycle. See [stage-0-orientation.md](references/stage-0-orientation.md).
2. **Mutate (Stage 1)**: classify the failure, propose one change, log friction events as they occur. See [mutation-protocol.md](references/mutation-protocol.md) and [stage-1-execution.md](references/stage-1-execution.md).
3. **Score (Stage 2)**: invoke `os-lab-scorer`. With a PEER_AGENT, the peer scores independently from its own session. See [stage-2-verification.md](references/stage-2-verification.md).
4. **Decide (Stage 3)**: KEEP is applied and committed; DISCARD writes a correction packet and re-signals the inner agent. See [stage-3-decision.md](references/stage-3-decision.md).
5. **Repeat** from step 2 until the cap, the target score or the budget guard.
6. **Close (Stage 4)**: friction gate, surveys, post-run metrics, session log, loop report, test registry, improvement ledger, then `os-memory-manager` for L3 promotion, auto-memory, Triple-Loop trigger check and lock release. See [stage-4-close.md](references/stage-4-close.md).

When the lab run is complete, hand the diff to `os-lab-backport` and the run record to `os-lab-log`.

## Verification

```bash
python scripts/post_run_metrics.py
```

Confirm a `metric` event was emitted, `friction` and `friction.resolved` counts match, and the ledger has a new row.

## References

- [mutation-protocol.md](references/mutation-protocol.md) - one iteration, proposer calls, second-order mutations.
- [stage-0-orientation.md](references/stage-0-orientation.md) - pre-flight reads and test registration.
- [stage-1-execution.md](references/stage-1-execution.md) - inner agent duties.
- [stage-2-verification.md](references/stage-2-verification.md) - independent scoring.
- [stage-3-decision.md](references/stage-3-decision.md) - KEEP and DISCARD handling.
- [stage-4-close.md](references/stage-4-close.md) - mandatory close checklist.
- [lab-limits.md](references/lab-limits.md) - budget guard, architecture, examples.
- [program.md](references/program.md) - example optimization program.
- [orchestrator-meta-survey.md](references/orchestrator-meta-survey.md) - multi-session retrospective.
- [cheapest_models.md](references/cheapest_models.md) - proposer model costs.
- [improvement-ledger-spec.md](references/memory/improvement-ledger-spec.md), [post_run_survey.md](references/memory/post_run_survey.md), [metrics.md](references/memory/metrics.md), [test-registry-protocol.md](references/testing/test-registry-protocol.md).
