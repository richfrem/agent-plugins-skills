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

## Current State vs Target State

Confirmed by red-team reviews (Gemini, Grok).

| File | Current state | Target state |
|---|---|---|
| `eval_runner.py` | Writes to `evals/results.tsv` on every call. `--json` flag outputs only `quality_score`, not f1. | Pure scorer. Writes nothing. `--json` outputs all fields: `{"quality_score": N, "accuracy": N, "f1": N, "heuristic": N}` |
| `evaluate.py` | Calls eval_runner twice (once `--json` for score, once probe for f1). Reads first BASELINE row (bug — f1 guard disabled). Writes to `autoresearch/results.tsv`. | Single call to eval_runner. Reads LAST BASELINE row. Writes one row to `<target-skill>/evals/results.tsv`. Exits 0 (KEEP) or 1 (DISCARD). |
| `evaluate.py` lock | Enforced by convention in program.md only | Runtime hash check at startup — aborts with error if `evaluate.py` or `eval_runner.py` have been modified since baseline |
| `autoresearch/results.tsv` | Separate duplicate ledger | Deleted — one ledger in `<target-skill>/evals/results.tsv` |
| `evals/results.tsv` (in skill-improvement-eval) | Self-eval rows + noisy probe rows (`_f1_probe`, `debug`) | Only rows written by evaluate.py. No probe rows. First corrupted BASELINE row (f1=0.0) removed. |
| `program.md` | In `skill-improvement-eval/references/` | In each target skill's `references/` |

## Known Risks

| Risk | Severity | Description |
|---|---|---|
| Baseline F1 guard disabled | Critical | `load_baseline()` reads first BASELINE row. First row has f1=0.0 (corrupted). F1 guard never triggers. Fix: read LAST BASELINE row. |
| Double evaluator call | High | `evaluate.py` calls eval_runner twice per iteration, creating noisy probe rows in results.tsv |
| eval_runner.py not pure | High | Writes side effects to results.tsv on every call, violating single responsibility |
| Meta-circular risk | Medium | This skill is being used to improve itself. Requires stricter safeguards on what the agent is allowed to change |
| Weak lock enforcement | Medium | Only program.md convention prevents agent from editing evaluate.py. No runtime check. |
