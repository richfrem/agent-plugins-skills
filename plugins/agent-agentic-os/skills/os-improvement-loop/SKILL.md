---
name: os-improvement-loop
plugin: agent-agentic-os
version: 0.5.0
description: >
  Pattern 5: Concurrent Event-Driven Multi-Agent Loop. Coordinates multiple Claude sessions
  as OS threads sharing a common event bus and memory address space. Every loop cycle is a
  full improvement cycle: execute, eval against benchmark (KEEP/DISCARD), emit friction events,
  and close with surveys, metrics, memory persistence, and Triple-Loop triggers.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Concurrent Agent Loop (`os-improvement-loop`)

Coordinates concurrent agent sessions as OS threads sharing a common event bus and memory address space to execute iterative improvement cycles.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **No Manual Rollback**: Never manually revert changes mid-cycle unless `evaluate.py` registers accuracy regression.
2. **Mandatory Eval Gate**: Every mutation must pass benchmark evaluation before merging (`evaluate.py` exit code 0).
3. **Session Close Protocol**: Always complete surveys, ledger updates, and memory promotions at cycle close.

## Quick start

Run a baseline evaluation on a target skill:

```bash
python3 scripts/evaluate.py --skill skills/todo-check/ --decision-only
```

## Workflow

1. **Stage 0 (Orientation)**: Read pre-flight state, verify event registry, and design the mutation packet.
2. **Stage 1 (Execution)**: Execute target task, log friction events, and perform local scoring.
3. **Stage 2 (Verification)**: Run independent peer evaluation via `evaluate.py`.
4. **Stage 3 (Decision)**: Issue KEEP or DISCARD verdict based on score deltas.
5. **Stage 4 (Close)**: Complete post-run surveys, ledger updates, and promote enduring facts via `os-memory-manager`.

## Verification

Confirm evaluation passes and handoff block is emitted:

```bash
python3 scripts/evaluate.py --skill skills/todo-check/
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for multi-agent improvement loops.
- [fallback-tree.md](references/fallback-tree.md) — Recovery procedures when agents stall or evaluations diverge.
- [stage-0-orientation.md](references/stage-0-orientation.md) — Pre-flight packet design protocols.
- [stage-4-close.md](references/stage-4-close.md) — Mandatory cycle close checklists and surveys.
