# Autoresearch Architecture

**Reference:** `references/research/karpathy-autoresearch-3-file-eval.md`
**Diagram:** `references/diagrams/autoresearch-loop.mmd`

---

## Purpose

`skill-improvement-eval` is a general-purpose evaluation SERVICE. It can run the Karpathy autoresearch loop against ANY skill in the ecosystem. The scripts live here. The data lives with each target skill.

---

## Karpathy 3-Component Mapping

| Karpathy Component | File | Purpose | Location |
|---|---|---|---|
| **1. The Spec** | | | |
| | `program.md` | Optimization goal, what is locked, NEVER STOP directive. Written once by human before loop starts. | `<target-skill>/references/program.md` |
| **2. The Mutation Target** | | | |
| | `SKILL.md` | The only file the agent changes each iteration. The trigger language being optimized. | `<target-skill>/SKILL.md` |
| **3. The Evaluator** | | Locked. Agent must never modify any part of this component. | |
| | `eval_runner.py` | Metric producer. Reads SKILL.md + evals.json, computes quality_score / accuracy / heuristic / f1. Pure scorer — outputs numbers only, writes nothing. | `skill-improvement-eval/scripts/eval_runner.py` |
| | `evaluate.py` | Loop gate. Calls eval_runner. Reads baseline from results.tsv. Compares score and f1. Writes one row to results.tsv. Exits 0 (KEEP) or 1 (DISCARD). | `skill-improvement-eval/scripts/evaluate.py` |
| | `evals.json` | Test prompts with expected trigger outcomes (true/false). The input eval_runner scores SKILL.md against. Written once by human. Never modified during loop. | `<target-skill>/evals/evals.json` |
| | `results.tsv` | Scoring history for this skill. One row per evaluation run. evaluate.py reads it for baseline; writes to it after each run. | `<target-skill>/evals/results.tsv` |
| **+ Loop Orchestrator** | | Not in Karpathy's original 3 — required to make the loop autonomous. | |
| | `train.py` | Drives iterations: reads program.md, calls agent to mutate SKILL.md, calls evaluate.py, handles KEEP/DISCARD git operations, loops forever. **MISSING — not yet built.** | `skill-improvement-eval/scripts/train.py` |

---

## Summary: Who Owns What

| Owned by | Files |
|---|---|
| **skill-improvement-eval** (scripts only) | `eval_runner.py`, `evaluate.py`, `train.py` |
| **Each target skill** (all data) | `SKILL.md`, `evals/evals.json`, `evals/results.tsv`, `references/program.md` |

The evaluation service owns no data. It only provides the tooling. Every target skill owns its own spec, test cases, mutation target, and scoring history.

---

## results.tsv Schema

Lives at `<target-skill>/evals/results.tsv`. One row per evaluation run for that skill.

| Column | Description |
|---|---|
| `timestamp` | ISO datetime of the run |
| `commit` | git short hash at time of run |
| `score` | final quality_score (0.0 - 1.0) |
| `baseline` | score of the first BASELINE row |
| `accuracy` | routing accuracy component |
| `heuristic` | structural health component |
| `f1` | F1 score (prevents keyword-stuffing) |
| `status` | BASELINE / KEEP / DISCARD |
| `description` | what was changed this iteration |

---

## Current State vs Target State

| File | Current state | Target state |
|---|---|---|
| `eval_runner.py` | Writes to target skill's evals/results.tsv (correct location, wrong ownership — it should not write, evaluate.py should) | Pure scorer, outputs only, writes nothing |
| `evaluate.py` | Calls eval_runner twice, writes to separate autoresearch/results.tsv | Single call to eval_runner, writes to target skill's evals/results.tsv |
| `train.py` | Does not exist | Loop orchestrator calling Claude CLI |
| `autoresearch/results.tsv` | Separate loop ledger (wrong — duplicate of evals/results.tsv) | Deleted |
| `program.md` | In skill-improvement-eval/references/ | In each target skill's references/ |
