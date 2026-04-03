# os-eval-runner

Autonomous skill optimization service based on the Karpathy autoresearch pattern.

Given any skill in the ecosystem, it can run an overnight loop that iteratively improves `SKILL.md` — scored entirely by code, no human in the loop, with automatic KEEP/DISCARD via git.

---

## Value

- **Objective**: Scores are computed by `eval_runner.py` against locked `evals.json` test prompts. No LLM subjectivity.
- **Exploit-proof**: Dual KEEP condition (`score >= baseline AND f1 >= baseline_f1`) prevents keyword-stuffing.
- **General-purpose**: One service evaluates any skill. Each target skill owns its own data.
- **Self-correcting**: DISCARD reverts `SKILL.md` via git. The loop never regresses.

---

## Quick Start

**Score a skill (standalone, no history written):**
```bash
python3 ./scripts/eval_runner.py --skill path/to/SKILL.md
python3 ./scripts/eval_runner.py --skill path/to/SKILL.md --json
```

**Establish a baseline for a target skill:**
```bash
python3 ./scripts/evaluate.py --skill path/to/SKILL.md --baseline --desc "initial baseline"
```

**Run one loop iteration (agent calls this after editing SKILL.md):**
```bash
python3 ./scripts/evaluate.py --skill path/to/SKILL.md --desc "what changed"
# exit 0 = KEEP  →  git add + commit
# exit 1 = DISCARD  →  git checkout -- SKILL.md
```

---

## How It Works

The agent IS the loop. There is no train.py. The agent reads `references/program.md`, edits `SKILL.md`, runs `evaluate.py`, handles KEEP/DISCARD, and repeats per the NEVER STOP directive.

```
Agent reads program.md
  -> edits SKILL.md (one change)
  -> python ./scripts/evaluate.py --skill SKILL.md
       -> ./scripts/eval_runner.py --json  (pure scorer, writes nothing)
       -> compares against last BASELINE in ./evals/results.tsv
       -> appends one row, exits 0 or 1
  -> KEEP: git commit  |  DISCARD: git checkout
  -> repeat
```

---

## Files

| File | Role |
|---|---|
| `SKILL.md` | Agent trigger definition + usage instructions |
| `scripts/eval_runner.py` | Pure metric producer — reads SKILL.md + evals.json, outputs score |
| `scripts/evaluate.py` | Loop gate — calls eval_runner, reads baseline, writes TSV row, exits 0/1 |
| `evals/evals.json` | Test prompts with expected trigger outcomes (locked during loop) |
| `evals/results.tsv` | Scoring history for this skill when used as a target |

Each **target skill** owns its own `evals/evals.json`, `evals/results.tsv`, and `references/program.md`. The scripts here are the shared service.

---

## Architecture & Background

- **Architecture doc**: `./references/autoresearch-architecture.md` — file ownership, schema, current vs target state, known risks
- **Overview**: `./references/autoresearch-overview.md` — how the Karpathy pattern maps to skills, worked example
- **Sequence diagram**: `./references/diagrams/autoresearch-loop.mmd`
- **Mapping diagram**: `./references/diagrams/mapping-karpathy-to-os-eval-runner.mmd`
- **Karpathy reference**: `<APS_ROOT>/plugins/agent-agentic-os/references/research/karpathy-autoresearch-3-file-eval.md`
