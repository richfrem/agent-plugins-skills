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

| Source | Priority | Content |
|--------|----------|---------|
| `context/experiment-log/index.md` | **Primary** | All logged runs; filter `result_type: numeric` for KEEP/DISCARD/score data from orchestrator runs |
| `context/memory/improvement-ledger.md` | Legacy fallback | Eval score progression written by os-improvement-loop Stage 4.7; used if experiment log has no numeric entries |
| `.agents/skills/*/evals/results.tsv` | Supplement | Per-skill detailed eval score history |

The experiment log is the unified source of truth for numeric results. The improvement ledger
is a legacy format maintained for backward compatibility with older loop runs.

---

## What It Produces

| Output | Description |
|--------|-------------|
| `context/memory/reports/progress_YYYYMMDD_HHMM.png` | Progress chart: KEEP/DISCARD timeline, running-best step line, change annotations |
| `context/memory/reports/summary_YYYYMMDD_HHMM.md` | Text summary: baseline vs best, top hits by delta, survey effectiveness, north star trend |

---

## Execution Flow

### Phase 0: Read experiment log for numeric entries

```bash
python3 plugins/agent-agentic-os/scripts/experiment_log.py summary
```

Then read `context/experiment-log/index.md` and filter for rows where the `Result Type`
column is `numeric`. For each matching row, read the linked `.md` file and extract from
its YAML header:

```
keeps:    (integer — from verdict string "NNK/NND ...")
discards: (integer)
baseline: (float)
best_score: (float)
delta:    (float, signed)
target:   (string — the skill/agent under test)
date:     (string)
```

Parse the verdict string with this pattern:
```
(\d+)K/(\d+)D baseline=([0-9.]+) best=([0-9.]+) delta=([+-][0-9.]+)
```

If 1+ numeric entries exist, use them as the primary data source for the chart.
If 0 numeric entries exist, fall through to Phase 1 (legacy ledger).

**Bridge step:** If the legacy `generate_report.py` script is being used, write the
extracted numeric data into `improvement-ledger.md` Section 1 format so the script
can consume it. Each numeric experiment log entry maps to one row:

```
| <date> | <target> | <baseline> | <best_score> | <delta> | <keeps> KEEP, <discards> DISCARD |
```

### Phase 1: Check legacy data availability (fallback only)

```bash
LEDGER="${CLAUDE_PROJECT_DIR}/context/memory/improvement-ledger.md"
if [ ! -f "$LEDGER" ]; then
  echo "No improvement ledger found. Run at least one full loop cycle first."
  echo "The ledger is created at Stage 4.7 of os-improvement-loop."
  exit 0
fi
wc -l "$LEDGER"
```

If the ledger exists but Section 1 table is empty (no rows beyond the header), inform the
user that no cycles have been completed yet and the first loop run will establish the baseline.
Do not run the report script on an empty ledger — it will produce an empty chart.

### Phase 2: Run the report

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$(pwd)/.agents/skills/agent-agentic-os}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

python "${PLUGIN_DIR}/skills/os-improvement-report/scripts/generate_report.py" \
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
python "$SCRIPT" --project-dir "$AGENTIC_OS_PROJECT" --plugin-dir "$AGENTIC_OS_PLUGIN"

# exploration-cycle cycles
python "$SCRIPT" --project-dir "$EXPLORATION_PROJECT" --plugin-dir "$EXPLORATION_PLUGIN"
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
   (see `references/memory/improvement-ledger-spec.md` — includes a bash init snippet).
2. Writing to Section 1 after every KEEP or DISCARD cycle.
3. Writing to Section 2 when a survey friction item results in a change attempt.
4. Writing to Section 3 once per session with the completion rate.

The `generate_report.py` script works on any ledger with this format — it is not
tied to agent-agentic-os specifically.

---

## References

- [improvement-ledger-spec.md](../../references/memory/improvement-ledger-spec.md) — ledger format, writing protocol, initialization
- [chart-reading-guide.md](references/operations/chart-reading-guide.md) — how to interpret KEEP/DISCARD dots, step line, and text summary fields
- [os-improvement-loop SKILL](../os-improvement-loop/SKILL.md) — Stage 4.7 writes to the ledger
- [test-scenarios-seed.md](../../references/testing/test-scenarios-seed.md) — 50 pre-designed test hypotheses
- [post_run_survey.md](../../references/memory/post_run_survey.md) — survey template (Section 2 trace sources)
