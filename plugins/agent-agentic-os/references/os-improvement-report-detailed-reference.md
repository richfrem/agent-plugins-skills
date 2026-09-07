# os-improvement-report — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Dependencies

Requires **Python 3.8+**, `pandas`, and `matplotlib`.

```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile.

## Phase 0: Read experiment log for numeric entries (full detail)

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

## Phase 1: Check legacy data availability (commands)

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

## Phase 2: Run the report (command)

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$(pwd)/.agents/skills/agent-agentic-os}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

python "${PLUGIN_DIR}/skills/os-improvement-report/scripts/generate_report.py" \
  --project-dir "$PROJECT_DIR" \
  --plugin-dir "$PLUGIN_DIR" \
  [--skill SESSION-MEMORY-MANAGER]   # optional: filter to one skill
```

The script exits 0 on success and prints the chart path and text summary to stdout.

## Phase 4: Cross-plugin reporting (optional, full detail)

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

## Adding a New Plugin

Any plugin that runs eval cycles can plug into this report by:

1. Initializing `context/memory/improvement-ledger.md` with the three-section format
   (see `references/memory/improvement-ledger-spec.md` — includes a bash init snippet).
2. Writing to Section 1 after every KEEP or DISCARD cycle.
3. Writing to Section 2 when a survey friction item results in a change attempt.
4. Writing to Section 3 once per session with the completion rate.

The `generate_report.py` script works on any ledger with this format — it is not
tied to agent-agentic-os specifically.
