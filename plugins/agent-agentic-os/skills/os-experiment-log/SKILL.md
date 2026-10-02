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

# OS Experiment Log

Unified cross-cutting persistent log for Agentic OS experiments, recording dated run entries to `context/experiment-log/` and indexing in `index.md`.

## Contents

- [Constraints](#constraints)
- [Source Types](#source-types-and-result-kinds)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Never mutate prior experiment log records; the log is append-only.
- Always verify `result_type` before parsing run outputs.
- Persist entries to `context/experiment-log/` and update `index.md` synchronously.

## Source Types and Result Kinds

Agents must check `result_type` before parsing:
- `verifier` (`qualitative`): PASS/PARTIAL/FAIL counts and handoff block validity.
- `tester` (`qualitative`): Scenario pass/fail criteria.
- `orchestrator` (`numeric`): Best score, baseline, score deltas, KEEP/DISCARD counts.
- `planner` (`qualitative`): Workstreams and identified gaps.
- `survey` (`mixed`): Friction counts and north-star metrics.

## Quick start

Query aggregate statistics across all logged experiments:

```bash
python3 scripts/experiment_log.py summary
```

## Workflow

1. **Resolve Mode**:
   - `append --source-type TYPE`: Persist newly completed experiment run.
   - `query <term>`: Search logged runs by keyword.
   - `summary`: Print cross-cutting aggregate metrics.
2. **Execute Operation**:
   ```bash
   python3 scripts/experiment_log.py append --source-type <type> --report <path> --session-id <id> --target <target> --triggered-by <caller>
   ```
3. **Confirm & Index**: Inspect `context/experiment-log/index.md` to confirm entry was recorded with valid header metadata.

## Verification

Verify log append and index sync with a query check:

```bash
python3 scripts/experiment_log.py query "<session-id>"
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Invocation templates, YAML schema, and smoke test scenarios.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Log format standards and validation requirements.
- [fallback-tree.md](references/fallback-tree.md) — Recovery procedures when logging or indexing fails.
