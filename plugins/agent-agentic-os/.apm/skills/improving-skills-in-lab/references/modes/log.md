# OS Lab Log

One skill for the lab's record keeping: write a run to the log, search the log, summarize it, and chart it.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> Persistent, append-only log of Skill Improvement Lab runs plus the charts and progress report built from it. Appends a dated entry to context/experiment-log/ after a run, queries past runs by keyword, prints aggregate summary counts, and renders the improvement trend chart (KEEP/DISCARD dots, running-best line) with generate_report.py. Use after any lab run to persist results before temp/ is cleared, and to answer "are we getting better?". Trigger phrases: "log this run", "append to the experiment log", "query the experiment log", "summarize all experiment runs", "show me the improvement chart", "progress report", "graph the eval scores", "what's the trend". DO NOT USE to run the improvement loop (use the `loop` mode), to score one skill change (use the `score` mode), to review or backport a lab diff (use the `backport` mode), or to write session memory (use the `memory` mode).

## Contents

- [Constraints](#constraints)
- [Source types](#source-types-and-result-kinds)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- The log is append-only. Never edit or delete prior entries in `context/experiment-log/`.
- Check `result_type` in an entry header before parsing it. `survey` entries are `mixed`.
- Write the entry file and update `index.md` in the same step.
- Reports are read-only views: write charts and summaries only to `context/memory/reports/`, using timestamped filenames.
- Primary data for charts is `context/experiment-log/index.md` (numeric rows) and per-skill `evals/results.tsv`; treat `context/memory/improvement-ledger.md` as a legacy fallback.
- If there are no numeric entries or completed cycles, report "No cycles completed yet" and do not render an empty chart.

## Source types and result kinds

| `--source-type` | `result_type` | Holds |
|---|---|---|
| `orchestrator` | numeric | Best score, baseline, delta, KEEP/DISCARD counts (a loop or scorer run) |
| `tester` | qualitative | Scenario pass/fail results |
| `verifier` | qualitative | PASS/PARTIAL/FAIL counts and handoff block validity |
| `planner` | qualitative | Workstreams and identified gaps |
| `survey` | mixed | Friction counts and north-star metrics |

## Quick start

```bash
# Aggregate counts across all logged runs
python3 scripts/experiment_log.py summary

# Progress chart and text summary for the workspace
python3 scripts/generate_report.py --project-dir . --plugin-dir <path-to-agent-agentic-os>
```

## Workflow

1. **Pick the mode.**
   - `append`: persist a completed run.
   - `query <term>`: search logged runs by keyword (session id, target, `FAIL`, `numeric`).
   - `summary`: aggregate counts by source type.
   - `report`: chart improvement across cycles (optionally `--skill <name>`).
2. **Append** right after a run, before `temp/` is cleared:
   ```bash
   python3 scripts/experiment_log.py append --source-type <type> --report <path> \
     --session-id <id> --target <target> --triggered-by <caller>
   ```
   `survey` needs no `--report`; every other type requires it. Fill in the `Actions Taken` placeholder afterwards.
3. **Confirm** the entry appears in `context/experiment-log/index.md` with a valid header.
4. **Report**: read numeric rows from the index and per-skill `results.tsv`, then run `generate_report.py`. It writes `progress_<timestamp>.png` and `summary_<timestamp>.md` to `context/memory/reports/`. Show the chart path, quote the highlights, and offer a per-skill drill-down with `--skill`.
5. **Interpret** with [chart-reading-guide.md](../chart-reading-guide.md): gray dots are DISCARD, green dots are KEEP, the green step line is the running best.

## Verification

```bash
python3 scripts/experiment_log.py query "<session-id>"
python3 scripts/generate_report.py --help
```

## References

- [detailed-reference.md](../log-detailed-reference.md): append command templates, entry format, smoke tests, gotchas.
- [report-reference.md](../report-reference.md): numeric-entry parsing, ledger bridge, cross-plugin reporting.
- [chart-reading-guide.md](../chart-reading-guide.md): how to read the chart.
- [improvement-ledger-spec.md](../improvement-ledger-spec.md): legacy ledger format.
- [acceptance-criteria.md](../acceptance-criteria.md#mode-log): trigger and output standards.
- [fallback-tree.md](../fallback-tree.md#mode-log): recovery when logging, indexing or charting fails.
