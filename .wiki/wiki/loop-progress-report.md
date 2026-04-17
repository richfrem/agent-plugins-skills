---
concept: loop-progress-report
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-improvement-report/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.165967+00:00
cluster: improvement
content_hash: 39134797a941aa88
---

# Loop Progress Report

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-improvement-report
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

| Source | Content |
|--------|---------|
| `context/memory/improvement-ledger.md` | Eval score progression (Section 1), survey-to-action trace (Section 2), north star metric (Section 3) |
| `.agents/skills/*/evals/results.tsv` | Per-skill detailed eval score history (supplement to ledger) |

The improvement ledger is the primary source. It is written at every loop close (Stage 4.7
of os-improvement-loop). See `references/memory/improvement-ledger-spec.md` for the format.

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

python3 "${PLUGIN_DIR}/skills/os-improvement-report/scripts/generate_report.py" \
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
Each pr

*(content truncated)*

## See Also

- [[triple-loop-architect-sibling-lab-setup]]
- [[triple-loop-orchestrator-unattended-supervisor]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[os-loop-command]]
- [[triple-loop-learning-system---architecture-overview]]
- [[loop-scheduler-and-heartbeat-pattern]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-improvement-report/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.165967+00:00
