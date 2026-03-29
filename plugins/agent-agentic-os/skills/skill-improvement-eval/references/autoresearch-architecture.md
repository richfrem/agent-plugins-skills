# Autoresearch Architecture

**Reference:** `references/research/karpathy-autoresearch-3-file-eval.md`
**Sequence Diagram:** `references/diagrams/autoresearch-loop.mmd`
**Mapping Diagram:** `references/diagrams/mapping-karpathy-to-skill-improvement-eval.mmd`

---

## Purpose

`skill-improvement-eval` is a general-purpose evaluation SERVICE. It can run the Karpathy autoresearch loop against ANY skill in the ecosystem. The scripts live here. The data lives with each target skill.

---

## Karpathy 3-Component Mapping

In Karpathy's original ML pattern:
- `train.py` is the mutation target — the script being optimized
- `prepare.py` is the locked evaluator — scores the mutation target
- The **agent** is the loop orchestrator — reads program.md, edits train.py, runs prepare.py, decides KEEP/DISCARD, repeats

There is no separate orchestrator script. The agent IS the loop.

| Karpathy Original | Our Implementation | File | Location |
|---|---|---|---|
| `program.md` | `program.md` | Spec: optimization goal, locked files, NEVER STOP | `<target-skill>/references/program.md` |
| `train.py` | `SKILL.md` | **Mutation target** — the only file the agent changes each iteration | `<target-skill>/SKILL.md` |
| _(input to prepare.py)_ | `evals.json` | Test prompts with expected trigger outcomes. The input the evaluator scores SKILL.md against. Written once, never modified during loop. | `<target-skill>/evals/evals.json` |
| `prepare.py` | `eval_runner.py` | **Metric producer** — reads SKILL.md + evals.json, computes quality_score / accuracy / heuristic / f1. Pure scorer, outputs numbers only, writes nothing. | `skill-improvement-eval/scripts/eval_runner.py` |
| `prepare.py` (gate logic) | `evaluate.py` | **Loop gate** — calls eval_runner, reads baseline from results.tsv, compares score and f1, writes one row to results.tsv, exits 0 (KEEP) or 1 (DISCARD). | `skill-improvement-eval/scripts/evaluate.py` |
| `results.tsv` | `results.tsv` | Scoring history for this skill. Baseline anchor + record of every iteration. evaluate.py reads it for baseline; writes to it after each run. | `<target-skill>/evals/results.tsv` |
| The agent | The agent | Loop orchestrator — reads program.md, edits SKILL.md, runs evaluate.py, handles KEEP/DISCARD git ops, loops forever per NEVER STOP directive. No script needed. | _(agent following program.md)_ |

---

## Why eval_runner.py and evaluate.py Are Both Needed

`prepare.py` in Karpathy's original does two things: produces the metric AND makes the KEEP/DISCARD decision. We split this into two scripts because `eval_runner.py` is general-purpose — it can score any SKILL.md standalone, outside any loop context. `evaluate.py` is loop-specific only.

| Script | Single responsibility | Usable outside loop |
|---|---|---|
| `eval_runner.py` | "What is the score of this SKILL.md?" | YES |
| `evaluate.py` | "Should the loop keep or discard this change?" | NO |

---

## Summary: Who Owns What

| Owner | Files | Purpose |
|---|---|---|
| **skill-improvement-eval** | `scripts/eval_runner.py` | Metric producer |
| **skill-improvement-eval** | `scripts/evaluate.py` | Loop gate |
| **Each target skill** | `SKILL.md` | Mutation target |
| **Each target skill** | `evals/evals.json` | Test prompts (what correct looks like) |
| **Each target skill** | `evals/results.tsv` | Scoring history |
| **Each target skill** | `references/program.md` | Loop spec |

The evaluation service owns only scripts. Every target skill owns all its own data.

---

## results.tsv Schema

Lives at `<target-skill>/evals/results.tsv`.

| Column | Description |
|---|---|
| `timestamp` | ISO datetime of the run |
| `commit` | git short hash at time of run |
| `score` | final quality_score (0.0 - 1.0) |
| `baseline` | score of the first BASELINE row |
| `accuracy` | routing accuracy component |
| `heuristic` | structural health component |
| `f1` | F1 score (prevents keyword-stuffing exploit) |
| `status` | BASELINE / KEEP / DISCARD |
| `description` | what was changed this iteration |

---

## v2 Changes (Fixed)

All items below were identified by red-team review (Gemini, Grok) and fixed in v2.

| Item | v1 Bug | v2 Fix |
|---|---|---|
| `eval_runner.py` purity | Wrote to TSV on every call; `--json` only output `quality_score` | Pure scorer — writes nothing; `--json` outputs all four fields |
| `evaluate.py` baseline read | Read first BASELINE row (f1=0.0 corrupted — F1 guard disabled) | Reads last BASELINE row; F1 guard active |
| `evaluate.py` double call | Called eval_runner twice per iteration (probe rows) | Single call; no probe rows |
| `evaluate.py` lock enforcement | Convention only (program.md) | Runtime `git status` check at startup — aborts if locked files modified |
| `evaluate.py` DISCARD revert | Agent responsible for `git checkout` (unreliable in long loops) | `evaluate.py` runs `git checkout -- SKILL.md` before `sys.exit(1)` |
| `evaluate.py` frontmatter fallback | Silently fell back to full file body if frontmatter malformed (stuffing exploit) | Fails hard — returns accuracy=0.0 if frontmatter missing or malformed |
| Ledger location | `autoresearch/results.tsv` (deleted duplicate) | `<target-skill>/evals/results.tsv` |
| Probe row pollution | `_f1_probe`, `debug` rows in evals/results.tsv | Cleaned; only real iteration rows remain |

## Known Risks (Remaining)

| Risk | Severity | Description |
|---|---|---|
| Meta-circular risk | Medium | This skill is used to improve itself. The lock check and frontmatter guard reduce this but cannot fully prevent an agent from modifying non-SKILL.md files in clever ways. |
| git status lock check scope | Low | Runtime check detects uncommitted modifications to locked files, but cannot detect modifications that were committed between iterations. A SHA256-at-baseline approach would close this gap fully. |
