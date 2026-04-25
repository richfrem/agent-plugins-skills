---
name: os-experiment-log
description: >
  Maintains a persistent log of evolution experiments and verification results.
  After any os-evolution-verifier run, appends the EVOLUTION_VERIFICATION block
  and run summary to context/experiment-log.md. Supports querying past results by
  scenario ID, path type, or verdict. Use to track what was tested, when, what
  passed or failed, and what actions were taken as a result.
argument-hint: "[append | query <term> | summary]"
tools: ["Bash"]
---

## Overview

Every time os-evolution-verifier runs, its EVOLUTION_VERIFICATION blocks and summary
should be persisted. This skill delegates to `scripts/experiment_log.py` — a Python
script that appends results to `context/experiment-log.md` so findings accumulate
across sessions rather than being lost when `temp/` is cleared.

---

## Phase 1 — Resolve Mode

Read the argument to determine mode:

- **`append`** (default): append latest test report to log
- **`query <term>`**: search log by scenario ID, verdict, or keyword
- **`summary`**: print aggregate stats across all runs

---

## Phase 2 — Execute

```bash
# Append latest test report (default — run after every verifier run)
python3 scripts/experiment_log.py append \
  --triggered-by os-evolution-verifier

# Append a specific report file
python3 scripts/experiment_log.py append \
  --report temp/os-evolution-verifier/test-report.md \
  --session-id 2026-04-25-round1 \
  --triggered-by os-evolution-verifier

# Query by scenario ID, verdict, or keyword
python3 scripts/experiment_log.py query T2-D
python3 scripts/experiment_log.py query FAIL

# Print aggregate summary
python3 scripts/experiment_log.py summary
```

---

## Phase 3 — Confirm and Report

After `append`:
```bash
tail -30 context/experiment-log.md
```
Report: "Appended [N] scenario results to `context/experiment-log.md`."

After `query`: relay matching entries with surrounding date and scenario context.

After `summary`: print the stats table verbatim.

---

## Log Format

`context/experiment-log.md` is append-only. Never truncate or overwrite it.
Each entry begins with `## Experiment Run — <date>` and ends with `---`.
The `### Actions Taken` section is filled in by the human or a follow-up agent
to record what was done in response to failures.

---

## Smoke Tests

**Smoke 1 — Append**: Run `python3 scripts/experiment_log.py append` after a verifier run.
Confirm last 10 lines of `context/experiment-log.md` contain `## Experiment Run`.

**Smoke 2 — Query**: Run `python3 scripts/experiment_log.py query PASS`.
Confirm output contains at least one EVOLUTION_VERIFICATION block.

**Smoke 3 — Summary**: Run `python3 scripts/experiment_log.py summary`.
Confirm output shows `Total runs:` and `Pass rate:` lines with numeric values.

---

## Gotchas

- **`temp/` is ephemeral**: If `temp/os-evolution-verifier/test-report.md` is missing
  after a shell restart, ask the user to re-run the verifier before appending. The script
  will exit with an error rather than appending empty data.

- **Actions Taken is human-filled**: The script writes the entry with a placeholder line.
  An experiment log without response actions is an audit trail, not a learning record.
  Always fill it in before the next run.

- **Do not summarize across partial data**: If `summary` returns all zeros, check that
  `context/experiment-log.md` exists and has at least one full run entry before reporting.
