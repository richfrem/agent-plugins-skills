# os-experiment-log — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Phase 2 — Execute (full command set)

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

## Smoke Tests

**Smoke 1 — Append verifier**: Run `python3 scripts/experiment_log.py append --source-type verifier`.
Confirm new `.md` file appears in `context/experiment-log/` and `index.md` has a new row.

**Smoke 2 — Query**: Run `python3 scripts/experiment_log.py query PASS`.
Confirm output lists at least one matching file with its header.

**Smoke 3 — Summary by type**: Run `python3 scripts/experiment_log.py summary`.
Confirm output shows `[verifier]`, `[orchestrator]` etc. sections with correct run counts.

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
