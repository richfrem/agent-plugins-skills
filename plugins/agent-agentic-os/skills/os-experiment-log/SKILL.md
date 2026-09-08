---
name: os-experiment-log
plugin: agent-agentic-os
description: >
  Maintains a persistent, folder-based log of all agentic-os experiment runs.
  Each run writes one dated file to context/experiment-log/ and updates index.md.
  Supports five source types: verifier (qualitative), tester (qualitative),
  orchestrator (numeric), planner (qualitative), survey (mixed).
  Handles both numeric results (eval scores, KEEP/DISCARD, delta) and qualitative
  results (PASS/FAIL/PARTIAL, gap analysis). Use after any experiment run to persist
  findings before temp/ is cleared.
argument-hint: "[append --source-type TYPE | query <term> | summary]"
tools: ["Bash"]
---

## Overview

The experiment log is the unified cross-cutting record for all agentic-os experiments.
One file per run, all files in `context/experiment-log/`, with `index.md` as a
queryable table of all runs.

```
context/experiment-log/
  index.md                                     ← one row per run (date, source, target, verdict)
  2026-04-25-verifier-os-architect-round1.md   ← from os-evolution-verifier
  2026-04-25-tester-os-architect.md            ← from os-architect-tester
  2026-04-25-os-improvement-loop-os-eval-runner.md    ← from os-improvement-loop
  2026-04-25-planner-0024.md                   ← from os-evolution-planner
  2026-04-25-survey-session.md                 ← from post_run_survey
```

## Source Types and Result Kinds

Agents must check `result_type` in a log entry's header before parsing it:

| `--source-type` | Produced by | `result_type` | Key fields |
|---|---|---|---|
| `verifier` | os-evolution-verifier | `qualitative` | PASS/PARTIAL/FAIL counts, HANDOFF_BLOCK validity |
| `tester` | os-architect-tester | `qualitative` | AC-1–4 pass/fail per scenario |
| `orchestrator` | os-improvement-loop | `numeric` | best_score, baseline, delta, KEEP/DISCARD counts |
| `planner` | os-evolution-planner | `qualitative` | workstream count, gaps identified |
| `survey` | post_run_survey | `mixed` | friction item count, north_star metric |

**Numeric entries** (`result_type: numeric`) carry quantitative metrics suitable for trending and charting.
**Qualitative entries** (`result_type: qualitative`) carry pass/fail verdicts and gap analysis prose.
**Mixed entries** (`result_type: mixed`) carry both — agents must check which fields are present before parsing.

## Phase 1 — Resolve Mode

Read the argument or invocation context to determine mode:

- **`append --source-type TYPE`**: log a new run from a completed experiment
- **`query <term>`**: search all files in `context/experiment-log/` by keyword
- **`summary`**: print aggregate stats across all runs, broken down by source type

## Phase 2 — Execute

Call `scripts/experiment_log.py append --source-type <type> --report <path> --session-id <id>
--target <target> --triggered-by <caller>` for each of the five source types, or `query <term>`
/ `summary` for lookups. Full example invocations for every source type are in
`references/detailed-reference.md`.

## Phase 3 — Confirm and Report

After `append`: run `tail -5 context/experiment-log/index.md` and report the logged filename.
After `query`: relay matching file names and their header blocks (date, source, target, verdict).
After `summary`: print the per-source-type breakdown verbatim.

## Log Entry Format, Smoke Tests, and Gotchas

The exact YAML-header + report file format, three smoke tests, and gotchas (mixed result-type
parsing, temp/ ephemerality, human-filled Actions Taken, intentional append-only duplicate rows)
are in `references/detailed-reference.md`.
