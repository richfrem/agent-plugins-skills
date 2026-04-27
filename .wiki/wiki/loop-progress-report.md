---
concept: loop-progress-report
source: plugin-code
source_file: agent-agentic-os/skills/os-improvement-report/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.718166+00:00
cluster: improvement
content_hash: bfbb0b729c1c67bf
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
Do not run the report script on an empty ledger — it will produce an empt

*(content truncated)*

## See Also

- [[broken-symlinks-repair-report]]
- [[concurrent-agent-loop]]
- [[dual-loop-innerouter-agent-delegation]]
- [[learning-loop]]
- [[learning-loop-retrospective-post-seal]]
- [[no-session-in-progress-suggest-starting-one]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-improvement-report/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.718166+00:00
