# Autoresearch Architecture

**Reference:** `references/research/karpathy-autoresearch-3-file-eval.md`
**Diagram:** `references/diagrams/autoresearch-loop.mmd`

---

## Purpose

`skill-improvement-eval` is a general-purpose evaluation SERVICE. It can run the Karpathy autoresearch loop against ANY skill in the ecosystem. The architecture must support evaluating many different target skills without mixing their data or coupling the service to any one target.

---

## Karpathy 3-Component Mapping

The autoresearch pattern has three required components. Every file in this system maps to exactly one of them.

| Karpathy Component | Role | Our Implementation | Lives in |
|---|---|---|---|
| **1. The Spec** (`program.md`) | Defines the goal, constraints, locked files, NEVER STOP directive. Human-authored once before the loop starts. | `references/program.md` | **Target skill** — each skill being optimized owns its own spec |
| **2. The Mutation Target** | The single file the agent is allowed to change each iteration. | `SKILL.md` | **Target skill** — the trigger language being optimized |
| **3. The Evaluator** | Locked. Produces a single numeric metric AND records whether the change is an improvement. Agent must never modify any part of this component. | `scripts/evaluate.py` + `scripts/eval_runner.py` + `evals/results.tsv` | **Evaluation service** — shared across all target skills |

### Evaluator Component: Three Parts

The evaluator is not a single file — it is three parts working together:

| Part | File | Responsibility |
|---|---|---|
| **Metric producer** | `scripts/eval_runner.py` | Pure scorer. Given a target SKILL.md and its evals.json, computes quality_score, accuracy, heuristic, f1. Outputs numbers only. Writes nothing. |
| **Loop gate** | `scripts/evaluate.py` | Reads baseline from results.tsv. Calls eval_runner. Compares score to baseline. Writes one row to results.tsv. Exits 0 (KEEP) or 1 (DISCARD). |
| **Evaluator memory** | `evals/results.tsv` | Central log across all target skills. evaluate.py reads it to know the baseline; writes to it to record the result. Without this, the loop cannot answer "is this better?" |

Both scripts are needed because the responsibilities are distinct:
- `eval_runner.py` answers: "what is the score of this SKILL.md?"
- `evaluate.py` answers: "should the loop keep or discard this change?"

`eval_runner.py` can also be used standalone outside any loop context (one-off scoring). `evaluate.py` is loop-specific only.

**Supporting file that enables the loop (not Karpathy's original 3, but required here):**

| File | Purpose | Lives in |
|---|---|---|
| `scripts/train.py` | Loop orchestrator (MISSING). Drives iterations: calls agent to mutate SKILL.md, calls evaluate.py, handles KEEP/DISCARD, loops. Equivalent to Karpathy's `claude --dangerously-skip-permissions` CLI call. | **Evaluation service** |
| `evals/evals.json` | Golden test cases defining correct routing for the target skill. Read by eval_runner. Never written to. | **Target skill** |

---

## Two Roles, Clearly Separated

| Role | Owner | What it contains |
|---|---|---|
| **Evaluation Service** | `skill-improvement-eval` | The scoring engine, loop orchestrator, central results log |
| **Target Skill** | any skill being optimized | Its own SKILL.md, its own golden test cases, its own loop spec |

The service reads from target skills. It never writes into them.

---

## File Matrix

### Evaluation Service Files
Live in `plugins/agent-agentic-os/skills/skill-improvement-eval/`

| File | Location | Purpose | Mutable during loop |
|---|---|---|---|
| `SKILL.md` | skill root | Trigger instructions for this skill itself | NO |
| `eval_runner.py` | `scripts/` | General scorer: reads target SKILL.md + target evals.json, outputs quality_score, accuracy, heuristic, f1 | NO - locked |
| `evaluate.py` | `scripts/` | Locked evaluator: calls eval_runner, reads baseline from central log, exits 0 (KEEP) or 1 (DISCARD) | NO - locked |
| `train.py` | `scripts/` | Loop orchestrator: reads program.md, calls agent to mutate target SKILL.md, calls evaluate.py, handles KEEP/DISCARD, loops forever | NO - locked |
| `evals/evals.json` | `evals/` | Routing test cases for THIS skill's own trigger (meta-eval only) | NO |
| `evals/results.tsv` | `evals/` | **Central log of every evaluation run by this service, across all target skills** | YES - appended per run |

### Target Skill Files
Live in `plugins/<plugin>/skills/<skill>/`

| File | Location | Purpose | Mutable during loop |
|---|---|---|---|
| `SKILL.md` | skill root | **THE MUTATION TARGET** - the only file the agent changes | YES - loop body |
| `evals/evals.json` | `evals/` | Golden test cases for this skill's routing accuracy | NO - locked, read-only |
| `references/program.md` | `references/` | Loop spec: what to optimize, what is locked, NEVER STOP | NO - set before loop starts |

---

## Central Results Log Schema

`evals/results.tsv` in the evaluation service — one row per evaluation run, across all target skills:

| Column | Description |
|---|---|
| `timestamp` | ISO datetime of the run |
| `commit` | git short hash at time of run |
| `skill_path` | relative path to the target SKILL.md being evaluated |
| `score` | final quality_score (0.0 - 1.0) |
| `baseline` | score of the BASELINE row for this skill |
| `accuracy` | routing accuracy component |
| `heuristic` | structural health component |
| `f1` | F1 score (prevents keyword-stuffing) |
| `status` | BASELINE / KEEP / DISCARD |
| `description` | what was changed this iteration |

The `skill_path` column is what makes this multi-skill capable — every row is identifiable to its target.

---

## What Lives Where: Decision Rules

**If a file is part of the scoring/orchestration infrastructure** → lives in the service (`skill-improvement-eval/scripts/`)

**If a file defines what "correct" means for a specific skill** → lives in the target skill (`<skill>/evals/evals.json`)

**If a file specifies the optimization goal for a specific skill** → lives in the target skill (`<skill>/references/program.md`)

**If a file records evaluation history** → lives in the service central log (`skill-improvement-eval/evals/results.tsv`), identified by `skill_path` column

**The service never writes into target skill directories.**

---

## The Missing Piece: train.py

`eval_runner.py` = Karpathy's `prepare.py` (scorer)
`evaluate.py` = Karpathy's `benchmark.mjs` (locked evaluator wrapper)
`train.py` = **MISSING** — the loop orchestrator

`train.py` is what makes the loop autonomous. It:

1. Takes a target skill path as argument
2. Reads the target skill's `references/program.md` for goal and constraints
3. Calls the agent (Claude CLI) with context: program.md + current SKILL.md + last N rows from central log for this skill
4. Agent makes one focused change to SKILL.md
5. Calls `evaluate.py --skill <path>`
6. If exit 0 (KEEP): `git add SKILL.md && git commit`
7. If exit 1 (DISCARD): `git checkout -- SKILL.md`
8. Loops (NEVER STOP until interrupted)

Without `train.py`, the loop requires a human to drive each iteration manually. With it, the loop runs overnight unattended.

---

## Current State vs Target State

| Item | Current state | Target state |
|---|---|---|
| `eval_runner.py` | Writes to target skill's evals/results.tsv | Writes to central log with skill_path column |
| `evaluate.py` | Calls eval_runner twice, writes own results.tsv | Single call, reads/writes central log only |
| `train.py` | Does not exist | Loop orchestrator calling Claude CLI |
| `evals/results.tsv` | Self-eval rows only, legacy column names | Central log for all target skills |
| `autoresearch/results.tsv` | Separate loop ledger (wrong) | Deleted - merged into central log |
| `program.md` | In this skill's references/ (wrong for other targets) | In each TARGET skill's references/ |
