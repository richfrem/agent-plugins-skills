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

### Layer 2: The Loop (scaffolded inside the target skill)

The actual autonomous optimization loop, scaffolded inside the target skill once it scores HIGH or MEDIUM.

```
<SKILLPATH>/
  references/
    program.md            <- the spec (goal, locked files, NEVER STOP)
  evals/
    evals.json            <- test prompts (locked during loop)
    results.tsv           <- loop ledger (one row per iteration)
```

The shared evaluation scripts (`evaluate.py`, `eval_runner.py`) live in the plugin's `scripts/` directory and are reused across all target skills.

---

## Concrete Example: skill-improvement-eval

> **Note:** The paths below are for `skill-improvement-eval` specifically.
> When applying this pattern to a different skill, replace the skill path throughout.
> Example skill root: `plugins/agent-agentic-os/skills/skill-improvement-eval/`

### Directory Layout

```
<SKILLPATH>/
  SKILL.md                     <- MUTATION TARGET: agent edits only this file
  evals/evals.json             <- test prompts (locked during loop)
  evals/results.tsv            <- loop ledger (one row per iteration)
  references/program.md        <- THE SPEC: goal, locked files, NEVER STOP

<plugin-root>/scripts/
  eval_runner.py               <- PURE SCORER: reads SKILL.md + evals.json, outputs JSON
  evaluate.py                  <- LOCKED GATE: calls scorer, reads baseline, writes TSV row, exits 0/1
```

### How One Loop Iteration Works

```
1. Agent reads <SKILLPATH>/references/program.md (goal: maximize quality_score)
2. Agent edits SKILL.md (one focused change per iteration)
3. Agent runs: python scripts/evaluate.py --skill <SKILLPATH>/SKILL.md --desc "what I changed"
4. evaluate.py:
     a. Checks locked files not modified (git status guard)
     b. Calls eval_runner.py --skill SKILL.md --json (single call)
     c. Parses {"quality_score": N, "accuracy": N, "f1": N, "heuristic": N}
     d. Reads baseline from <SKILLPATH>/evals/results.tsv (last BASELINE row)
     e. Compares score AND f1 against baseline (dual guard)
     f. Writes one row to <SKILLPATH>/evals/results.tsv
     g. DISCARD: runs git checkout -- SKILL.md, exits 1
     h. KEEP: exits 0
5. KEEP:    agent runs git add SKILL.md && git commit -m "keep: score=X <description>"
6. Repeat (NEVER STOP)
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
| `<SKILLPATH>/evals/evals.json` | Test prompts with expected trigger outcomes | Nobody during the loop (locked) |
| `<SKILLPATH>/evals/results.tsv` | Loop ledger — one row per iteration | `evaluate.py` (appends only) |
| `<SKILLPATH>/references/program.md` | Spec: goal, locked files, NEVER STOP | Human (written once before loop starts) |
| `<plugin-root>/scripts/eval_runner.py` | Pure scorer: reads SKILL.md + evals.json, outputs JSON | Nobody during the loop (locked) |
| `<plugin-root>/scripts/evaluate.py` | Loop gate: calls scorer, reads baseline, exits 0/1, reverts on DISCARD | Nobody (locked) |

---

## What "Locked" Means in Practice

`references/program.md` declares which files are locked:

```
Locked: scripts/evaluate.py, scripts/eval_runner.py, evals/evals.json
```

Without these locks, an agent would inevitably:
- Rewrite `evaluate.py` to return 1.0 for any input (Goodhart's Law)
- Delete hard test cases from `evals.json` to inflate accuracy
- Lower the KEEP threshold so every run passes

The lock on the evaluator is what makes the metric trustworthy. The agent's only lever is SKILL.md.

---

## The Loop vs The Evals (Easy to Confuse)

| | `evals/evals.json` | `scripts/evaluate.py` |
|---|---|---|
| **Purpose** | Test prompts with expected trigger outcomes | Loop gate: scores SKILL.md and decides KEEP/DISCARD |
| **Run by** | CI / `run_eval.py` | The autoresearch loop agent |
| **Mutable** | NO (locked during loop) | NO (locked evaluator) |
| **Output** | Pass/fail per trigger scenario | exit 0 (KEEP) or exit 1 (DISCARD) |

`evals.json` defines WHAT to test. `evaluate.py` calls `eval_runner.py` to score against it.

There is one `results.tsv` per target skill — `<target-skill>/evals/results.tsv` — written only by `evaluate.py`, one row per loop iteration.

---

## Summary

```
Karpathy autoresearch pattern
    |
    v
eval-autoresearch-fit skill       <- "is this skill worth looping on?"
    | scores HIGH or MEDIUM
    v
scaffold inside <SKILLPATH>
    |
    +-- references/program.md    (spec: goal, locked files, NEVER STOP)
    +-- evals/evals.json         (test prompts — locked)
    +-- evals/results.tsv        (ledger: one row per iteration)
    |
    v
Agent loop:
    edit <SKILLPATH>/SKILL.md
    -> python scripts/evaluate.py --skill <SKILLPATH>/SKILL.md
    -> KEEP: git commit | DISCARD: evaluate.py reverts automatically
    -> repeat forever
```

The bottleneck is not running the loop. The bottleneck is `program.md`: knowing what to measure and setting the right constraints.
