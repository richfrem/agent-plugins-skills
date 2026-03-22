---
name: loop-progress-report
description: >
  Trigger with "show me the improvement chart", "how are we improving", "progress report",
  "graph the eval scores", "show cycle of improvement", "what's the trend", "are we getting
  better", "show improvement over time", "generate the progress chart", "are we improving",
  "what did this cycle contribute", or any time the user wants a visual or text summary of
  how the agentic loop is improving across cycles. Use this skill even when the user says
  "show me the data" or "how are we doing overall" in the context of an improvement loop.
  Works across all plugins that write to an improvement-ledger.md. Do NOT use this to run
  the learning loop or to evaluate a specific skill change -- use os-learning-loop or
  skill-improvement-eval for those.

  <example>
  Context: User wants to see if the agentic-os skills are getting better over cycles.
  user: "Show me the improvement chart. Are we actually getting better?"
  assistant: "I'll run the loop-progress-report to generate the progress chart and summary."
  <commentary>
  User wants the longitudinal view — generate_report.py reads improvement-ledger.md and produces
  the progress.png chart (KEEP/DISCARD timeline with running-best line) and text summary.
  </commentary>
  </example>

  <example>
  Context: End of a session, user wants to see what this cycle contributed.
  user: "What did we actually improve this session?"
  assistant: "I'll run the progress report to show this cycle's contribution to the improvement trend."
  <commentary>
  Report includes per-skill score delta, survey-to-action trace, and north star completion rate.
  </commentary>
  </example>

  <example>
  Context: User asks generally about progress but doesn't want the report run.
  user: "How does the improvement tracking work?"
  assistant: "The improvement ledger tracks three things: eval score progression per skill (like the
  autoresearch progress chart), a survey-to-action trace connecting friction items to score changes,
  and the North Star completion rate. The loop-progress-report skill reads it and produces a chart."
  <commentary>User wants explanation, not execution. Do not run generate_report.py.</commentary>
  </example>
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+**, `pandas`, and `matplotlib`.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile.

---

# Loop Progress Report

Visual and text reporting on the agentic loop improvement cycle — across any plugin that
maintains an `improvement-ledger.md` and `results.tsv` per skill.

The reference output is the autoresearch progress chart: green KEEP dots on a timeline,
gray DISCARD dots, running-best step line, annotations showing what each improvement was.
This skill produces the same chart for agentic-os and exploration-cycle-plugin improvement cycles.

---

## What It Reads

| Source | Content |
|--------|---------|
| `context/memory/improvement-ledger.md` | Eval score progression (Section 1), survey-to-action trace (Section 2), north star metric (Section 3) |
| `plugins/*/skills/*/evals/results.tsv` | Per-skill detailed eval score history (supplement to ledger) |

The improvement ledger is the primary source. It is written at every loop close (Stage 4.7
of concurrent-agent-loop). See `references/improvement-ledger-spec.md` for the format.

---

## What It Produces

| Output | Description |
|--------|-------------|
| `context/memory/reports/progress_YYYYMMDD_HHMM.png` | Progress chart: KEEP/DISCARD timeline, running-best step line, change annotations |
| `context/memory/reports/summary_YYYYMMDD_HHMM.md` | Text summary: baseline vs best, top hits by delta, survey effectiveness, north star trend |

---

## Execution Flow

### Phase 1: Check data availability

```bash
LEDGER="${CLAUDE_PROJECT_DIR}/context/memory/improvement-ledger.md"
if [ ! -f "$LEDGER" ]; then
  echo "No improvement ledger found. Run at least one full loop cycle first."
  echo "The ledger is created at Stage 4.7 of concurrent-agent-loop."
  exit 0
fi
wc -l "$LEDGER"
```

If the ledger exists but Section 1 table is empty (no rows beyond the header), inform the
user that no cycles have been completed yet and the first loop run will establish the baseline.
Do not run the report script on an empty ledger — it will produce an empty chart.

### Phase 2: Run the report

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$(pwd)/plugins/agent-agentic-os}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

python3 "${PLUGIN_DIR}/skills/loop-progress-report/scripts/generate_report.py" \
  --project-dir "$PROJECT_DIR" \
  --plugin-dir "$PLUGIN_DIR" \
  [--skill SESSION-MEMORY-MANAGER]   # optional: filter to one skill
```

The script exits 0 on success and prints the chart path and text summary to stdout.

### Phase 3: Surface the output

After the script completes:

1. Report the chart path to the user: `context/memory/reports/progress_[TIMESTAMP].png`
2. Print the text summary inline (it is concise — top hits table, north star trend).
3. Ask: "Would you like me to open the chart image or show the per-skill detail?"

### Phase 4: Cross-plugin reporting (optional)

If the user wants improvement tracking across both `agent-agentic-os` AND `exploration-cycle-plugin`,
run the report twice — once per plugin — passing each plugin's project dir:

```bash
# agentic-os cycles
python3 "$SCRIPT" --project-dir "$AGENTIC_OS_PROJECT" --plugin-dir "$AGENTIC_OS_PLUGIN"

# exploration-cycle cycles
python3 "$SCRIPT" --project-dir "$EXPLORATION_PROJECT" --plugin-dir "$EXPLORATION_PLUGIN"
```

Both plugins write to `context/memory/improvement-ledger.md` in their respective project dirs.
Each produces its own chart. The text summaries can be concatenated for a combined view.

---

## Reading the Chart

The chart mirrors the autoresearch progress.png:

- **X-axis**: Cycle number (chronological order)
- **Y-axis**: Eval score for the target skill (higher = better)
- **Gray dots**: DISCARD cycles — attempts that did not improve the skill
- **Green dots**: KEEP cycles — improvements that stuck
- **Green step line**: Running best — the frontier of improvement over time
- **Annotations**: What change was made on each KEEP cycle

A flat or declining step line = the loop is not improving the skill.
Frequent DISCARD clusters = hypothesis quality needs work (check test scenarios seed).
Steep step-line rises = the survey-to-action trace is working.

---

## Adding a New Plugin

Any plugin that runs eval cycles can plug into this report by:

1. Initializing `context/memory/improvement-ledger.md` with the three-section format
   (see `references/improvement-ledger-spec.md` — includes a bash init snippet).
2. Writing to Section 1 after every KEEP or DISCARD cycle.
3. Writing to Section 2 when a survey friction item results in a change attempt.
4. Writing to Section 3 once per session with the completion rate.

The `generate_report.py` script works on any ledger with this format — it is not
tied to agent-agentic-os specifically.

---

## References

- [improvement-ledger-spec.md](../../references/improvement-ledger-spec.md) — ledger format, writing protocol, initialization
- [chart-reading-guide.md](references/chart-reading-guide.md) — how to interpret KEEP/DISCARD dots, step line, and text summary fields
- [concurrent-agent-loop SKILL](../concurrent-agent-loop/SKILL.md) — Stage 4.7 writes to the ledger
- [test-scenarios-seed.md](../../references/test-scenarios-seed.md) — 50 pre-designed test hypotheses
- [post_run_survey.md](../../references/post_run_survey.md) — survey template (Section 2 trace sources)
