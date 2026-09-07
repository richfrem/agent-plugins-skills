---
name: os-improvement-report
plugin: agent-agentic-os
description: >
  Trigger with "show me the improvement chart", "how are we improving", "progress report",
  "graph the eval scores", "show cycle of improvement", "what's the trend", "are we getting
  better". Produces a visual/text summary of how the agentic loop is improving across cycles.
  Do NOT use this to run the learning loop or evaluate a specific skill change.
allowed-tools: Bash, Read, Write
---

# Loop Progress Report

Visual and text reporting on the agentic loop improvement cycle — across any plugin that
maintains an `improvement-ledger.md` and `results.tsv` per skill.

The reference output is the autoresearch progress chart: green KEEP dots on a timeline,
gray DISCARD dots, running-best step line, annotations showing what each improvement was.
This skill produces the same chart for agentic-os and exploration-cycle-plugin improvement cycles.

Dependencies (Python 3.8+, pandas, matplotlib) are in `references/detailed-reference.md`.

## What It Reads

| Source | Priority | Content |
|--------|----------|---------|
| `context/experiment-log/index.md` | **Primary** | All logged runs; filter `result_type: numeric` for KEEP/DISCARD/score data from orchestrator runs |
| `context/memory/improvement-ledger.md` | Legacy fallback | Eval score progression written by os-improvement-loop Stage 4.7; used if experiment log has no numeric entries |
| `.agents/skills/*/evals/results.tsv` | Supplement | Per-skill detailed eval score history |

The experiment log is the unified source of truth for numeric results. The improvement ledger
is a legacy format maintained for backward compatibility with older loop runs.

## What It Produces

| Output | Description |
|--------|-------------|
| `context/memory/reports/progress_YYYYMMDD_HHMM.png` | Progress chart: KEEP/DISCARD timeline, running-best step line, change annotations |
| `context/memory/reports/summary_YYYYMMDD_HHMM.md` | Text summary: baseline vs best, top hits by delta, survey effectiveness, north star trend |

## Execution Flow

1. **Read experiment log for numeric entries** — run `experiment_log.py summary`, filter
   `context/experiment-log/index.md` for `Result Type: numeric` rows, and parse each linked
   file's KEEP/DISCARD verdict string. Fall through to Phase 1 if no numeric entries exist.
   Full parsing detail in `references/detailed-reference.md`.
2. **Check legacy data availability (fallback only)** — if `context/memory/improvement-ledger.md`
   is missing or its Section 1 table is empty, tell the user no cycles have completed yet rather
   than running the report on an empty ledger.
3. **Run the report** — invoke `generate_report.py --project-dir ... --plugin-dir ...`
   (optionally `--skill <name>`). Exits 0 and prints the chart path + text summary.
4. **Surface the output** — report the chart path, print the text summary inline, and ask
   whether to open the chart image or show per-skill detail.
5. **Cross-plugin reporting (optional)** — if tracking both `agent-agentic-os` and
   `exploration-cycle-plugin`, run the report once per plugin's project dir and concatenate the
   text summaries. Full commands in `references/detailed-reference.md`.

How to read the resulting chart, and how any other plugin can plug into this report via the
three-section ledger format, are in `references/detailed-reference.md`.

## References

- [improvement-ledger-spec.md](../../references/memory/improvement-ledger-spec.md) — ledger format, writing protocol, initialization
- [chart-reading-guide.md](references/operations/chart-reading-guide.md) — how to interpret KEEP/DISCARD dots, step line, and text summary fields
- [os-improvement-loop SKILL](../os-improvement-loop/SKILL.md) — Stage 4.7 writes to the ledger
- [test-scenarios-seed.md](../../references/testing/test-scenarios-seed.md) — 50 pre-designed test hypotheses
- [post_run_survey.md](../../references/memory/post_run_survey.md) — survey template (Section 2 trace sources)
