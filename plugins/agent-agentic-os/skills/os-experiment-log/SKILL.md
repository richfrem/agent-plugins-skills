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

---

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

---

## Phase 1 — Resolve Mode

Read the argument or invocation context to determine mode:

- **`append --source-type TYPE`**: log a new run from a completed experiment
- **`query <term>`**: search all files in `context/experiment-log/` by keyword
- **`summary`**: print aggregate stats across all runs, broken down by source type

---

## Phase 2 — Execute

```bash
# After os-evolution-verifier run
python3 scripts/experiment_log.py append \
  --source-type verifier \
  --report temp/os-evolution-verifier/test-report.md \
  --session-id 2026-04-25-round1 \
  --target os-architect \
  --triggered-by os-evolution-verifier

# After os-architect-tester run
python3 scripts/experiment_log.py append \
  --source-type tester \
  --report temp/test_report_consolidated.md \
  --session-id 2026-04-25-tester \
  --target os-architect \
  --triggered-by os-architect-tester

# After os-improvement-loop run (numeric — has score delta)
python3 scripts/experiment_log.py append \
  --source-type orchestrator \
  --report temp/logs/run-log.md \
  --session-id 2026-04-25-os-eval-runner \
  --target os-eval-runner \
  --triggered-by os-improvement-loop

# After os-evolution-planner writes a task plan
python3 scripts/experiment_log.py append \
  --source-type planner \
  --report tasks/todo/0024-plan.md \
  --session-id 0024 \
  --target os-eval-runner \
  --triggered-by os-evolution-planner

# After a post-run survey
python3 scripts/experiment_log.py append \
  --source-type survey \
  --session-id 2026-04-25-session \
  --target session \
  --triggered-by human

# Query by term
python3 scripts/experiment_log.py query T2-D
python3 scripts/experiment_log.py query FAIL
python3 scripts/experiment_log.py query numeric

# Aggregate summary
python3 scripts/experiment_log.py summary
```

---

## Phase 3 — Confirm and Report

After `append`:
```bash
tail -5 context/experiment-log/index.md
```
Report: "Logged to `context/experiment-log/<filename>`. Index updated."

After `query`: relay matching file names and their header blocks (date, source, target, verdict).

After `summary`: print the per-source-type breakdown verbatim.

---

## Log Entry Format

Each file has a YAML-like header fence followed by the full report:

```
---
type: verifier
result_type: qualitative
date: 2026-04-25 15:12
session_id: 2026-04-25-round1
source: os-evolution-verifier
target: os-architect
verdict: 8P/0Pa/0F of 8
---

## Experiment — 2026-04-25 15:12 | verifier | os-architect

| Field | Value |
...

[full report content]

### Actions Taken
_[fill in: spec fix, new eval, new skill]_
```

---

## Smoke Tests

**Smoke 1 — Append verifier**: Run `python3 scripts/experiment_log.py append --source-type verifier`.
Confirm new `.md` file appears in `context/experiment-log/` and `index.md` has a new row.

**Smoke 2 — Query**: Run `python3 scripts/experiment_log.py query PASS`.
Confirm output lists at least one matching file with its header.

**Smoke 3 — Summary by type**: Run `python3 scripts/experiment_log.py summary`.
Confirm output shows `[verifier]`, `[orchestrator]` etc. sections with correct run counts.

---

## Gotchas

- **Never parse `result_type: mixed` with numeric-only logic**: The `survey` source type
  contains both friction prose and numeric north_star values. Always check `result_type`
  in the file header before assuming field presence.

- **`temp/` is ephemeral**: Call `append` immediately after a run completes, before any
  shell restart. The script exits with an error if the report file is missing rather than
  appending empty data.

- **Actions Taken is human-filled**: The script writes a placeholder. An experiment log
  without response actions is an audit trail, not a learning record. Fill it in before
  the next run.

- **Duplicate index rows**: If `append` is called twice for the same session, two rows
  appear in `index.md`. This is intentional (the file is append-only) but worth noting
  when querying.
