# Autoresearch Overview: Applying the Karpathy Loop to Skills

**Reference:** `<repo-root>/plugins/agent-agentic-os/references/research/karpathy-autoresearch-3-file-eval.md`
**Sequence Diagram:** `references/diagrams/autoresearch-loop.mmd`
**Mapping Diagram:** `references/diagrams/mapping-karpathy-to-skill-improvement-eval.mmd`

---

## The Big Picture

Karpathy's autoresearch pattern says: if you have a single objective metric, an automated evaluator, and one mutable file, you can run an autonomous overnight loop to optimize anything.

This document describes how that pattern is applied to **skill files** (SKILL.md) in the plugin ecosystem — using `skill-improvement-eval` as the concrete worked example.

The goal: can an agent iteratively improve how reliably a skill triggers and performs, without any human in the loop, scored entirely by code?

---

## Two-Layer System

There are two distinct roles:

### Layer 1: Assessment (eval-autoresearch-fit)

A one-time scoring pass that answers: "Is this skill worth running through the Karpathy loop?"

Scores each skill 0-40 across four dimensions (objectivity, execution speed, frequency, utility) and outputs a verdict (HIGH / MEDIUM / LOW / NOT_VIABLE). This skill does NOT run the loop — it decides whether a loop is worth building.

> Example location (this is one possible placement — not a required path):
> `plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/`

### Layer 2: The Loop (autoresearch/ inside the target skill)

The actual autonomous optimization loop, scaffolded inside the target skill once it scores HIGH or MEDIUM.

```
<SKILLPATH>/
  autoresearch/
    program.md    <- the spec
    evaluate.py   <- locked evaluator
    results.tsv   <- experiment ledger
```

---

## Concrete Example: skill-improvement-eval

> **Note:** The paths below are for `skill-improvement-eval` specifically.
> When applying this pattern to a different skill, replace the skill path throughout.
> Example skill root: `plugins/agent-agentic-os/skills/skill-improvement-eval/`

### Directory Layout

```
<SKILLPATH>/
  SKILL.md                          <- MUTATION TARGET: agent edits only this file
  scripts/eval_runner.py            <- scoring engine (keyword routing + heuristics)
  evals/evals.json                  <- golden test cases (locked during loop)
  evals/results.tsv                 <- eval_runner's own output log
  autoresearch/
    program.md                      <- THE SPEC: goal, constraints, NEVER STOP
    evaluate.py                     <- LOCKED EVALUATOR: runs scorer, records KEEP/DISCARD
    eval_runner.py -> ../scripts/   <- symlink for visibility (not a separate file)
    results.tsv                     <- loop experiment ledger (one row per iteration)
```

### How One Loop Iteration Works

```
1. Agent reads autoresearch/program.md (goal: maximize quality_score)
2. Agent edits SKILL.md (one focused change per iteration)
3. Agent runs: python autoresearch/evaluate.py --desc "what I changed"
4. evaluate.py:
     a. Calls scripts/eval_runner.py --skill SKILL.md --json
     b. Parses {"quality_score": 0.8444}
     c. Reads baseline from autoresearch/results.tsv (first BASELINE row)
     d. Compares score and f1 against baseline
     e. Writes row to autoresearch/results.tsv: timestamp, commit, score, baseline, f1, KEEP/DISCARD
     f. Exits 0 (KEEP) or 1 (DISCARD)
5. KEEP:    git add <SKILLPATH>/SKILL.md && git commit -m "keep: score=X <description>"
6. DISCARD: git checkout -- <SKILLPATH>/SKILL.md
7. Repeat (NEVER STOP)
```

### The Metric (skill-improvement-eval specific)

```
quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)
```

- `routing_accuracy`: fraction of `evals.json` prompts correctly routed via keyword overlap against SKILL.md frontmatter
- `heuristic_score`: structural health check (has `<example>` blocks, minimum content length)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  - Dual condition prevents keyword-stuffing exploits (padding triggers raises recall but drops F1)

### Baseline (established 2026-03-28, commit abeb626)

| metric | value |
|---|---|
| score | 0.8444 |
| f1 | 0.8333 |
| commit | abeb626 |
| status | BASELINE |

---

## File Roles (Generic)

When applying this pattern to any skill, map the files as follows:

| File | Role | Who touches it |
|---|---|---|
| `<SKILLPATH>/SKILL.md` | Mutation target — the only file the agent changes | Agent (loop body only) |
| `<SKILLPATH>/evals/evals.json` | Golden test cases | Nobody during the loop (locked) |
| `<SKILLPATH>/scripts/eval_runner.py` | Scoring engine | Nobody during the loop (locked) |
| `<SKILLPATH>/autoresearch/program.md` | Spec: goal, constraints, NEVER STOP | Human (written once before loop starts) |
| `<SKILLPATH>/autoresearch/evaluate.py` | Locked evaluator: runs scorer, writes KEEP/DISCARD | Nobody (locked) |
| `<SKILLPATH>/autoresearch/results.tsv` | Loop experiment ledger | `evaluate.py` (appends one row per iteration) |

---

## What "Locked" Means in Practice

`autoresearch/program.md` declares which files are locked:

```
Locked: autoresearch/evaluate.py, evals/evals.json, scripts/eval_runner.py
```

Without these locks, an agent would inevitably:
- Rewrite `evaluate.py` to return 1.0 for any input (Goodhart's Law)
- Delete hard test cases from `evals.json` to inflate accuracy
- Lower the KEEP threshold so every run passes

The lock on the evaluator is what makes the metric trustworthy. The agent's only lever is SKILL.md.

---

## The Loop vs The Evals (Easy to Confuse)

| | `evals/evals.json` | `autoresearch/evaluate.py` |
|---|---|---|
| **Purpose** | Tests whether the skill TRIGGERS correctly | Measures how GOOD the SKILL.md instructions are |
| **Run by** | CI / `run_eval.py` | The autoresearch loop agent |
| **Mutable** | NO (locked during loop) | NO (locked evaluator) |
| **Output** | Pass/fail per trigger scenario | A single quality_score float |

`evals.json` defines WHAT to test. `evaluate.py` uses it AS the benchmark.

There are also two `results.tsv` files — different things:
- `evals/results.tsv` — eval_runner's own log, written on every eval_runner call
- `autoresearch/results.tsv` — the loop ledger, one row per agent iteration

---

## Summary

```
Karpathy autoresearch pattern
    |
    v
eval-autoresearch-fit skill       <- "is this skill worth looping on?"
    | scores HIGH or MEDIUM
    v
scaffold autoresearch/ inside <SKILLPATH>
    |
    +-- program.md    (spec: what to optimize, what is locked, NEVER STOP)
    +-- evaluate.py   (locked evaluator: runs scorer, records KEEP/DISCARD)
    +-- results.tsv   (ledger: one row per iteration)
    |
    v
Agent loop:
    edit <SKILLPATH>/SKILL.md
    -> python autoresearch/evaluate.py
    -> KEEP: git commit | DISCARD: git checkout
    -> repeat forever
```

The bottleneck is not running the loop. The bottleneck is `program.md`: knowing what to measure and setting the right constraints.
