# How This Experiment Applies the Karpathy Autoresearch Pattern to Skills

**Reference:** `plugins/agent-agentic-os/references/research/karpathy-autoresearch-3-file-eval.md`

---

## The Big Picture

Karpathy's autoresearch pattern says: if you have a single objective metric, an automated evaluator, and one mutable file, you can run an autonomous overnight loop to optimize anything.

This experiment applies that pattern to **skill files** (SKILL.md) in the plugin ecosystem.

The goal: can an agent iteratively improve how reliably a skill triggers and performs, without any human in the loop, scored entirely by code?

---

## Two-Layer System

There are two distinct roles in this experiment:

### Layer 1: Assessment (this skill - eval-autoresearch-fit)

**What:** `plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/`

**Purpose:** A one-time scoring pass. Answers the question: "Is this skill a good candidate to run through the Karpathy loop?"

**Output:** A score (0-40) across four dimensions and a verdict (HIGH/MEDIUM/LOW/NOT_VIABLE) stored in:
`assets/resources/summary-ranked-skills.json`

This skill does NOT run the loop itself. It decides WHETHER a loop is worth building.

### Layer 2: The Loop (autoresearch/ inside each target skill)

**What:** `plugins/<plugin>/skills/<skill>/autoresearch/`

**Purpose:** The actual autonomous optimization loop, scaffolded inside the target skill once it scores HIGH or MEDIUM.

**Mutation target:** `SKILL.md` (one focused change per iteration)

---

## Concrete Example: skill-improvement-eval

The first skill scaffolded with the autoresearch loop:

```
plugins/agent-agentic-os/skills/skill-improvement-eval/
  SKILL.md                          <- MUTATION TARGET (agent edits this each iteration)
  scripts/eval_runner.py            <- scoring engine (keyword routing + heuristics)
  evals/evals.json                  <- golden test cases (9 prompts, expected trigger/no-trigger)
  evals/results.tsv                 <- eval_runner output log
  autoresearch/
    program.md                      <- THE SPEC: goal, constraints, NEVER STOP
    evaluate.py                     <- LOCKED EVALUATOR: runs eval_runner, records KEEP/DISCARD
    eval_runner.py -> ../scripts/   <- symlink so the loop is self-contained
    results.tsv                     <- loop experiment ledger (commit, score, baseline, status)
```

### How One Loop Iteration Works

```
1. Agent reads program.md (goal: maximize quality_score)
2. Agent edits SKILL.md (one change: add example, reword trigger phrase, etc.)
3. Agent runs: python autoresearch/evaluate.py --desc "what I changed"
4. evaluate.py:
     a. Calls eval_runner.py --skill SKILL.md --json
     b. Parses {"quality_score": 0.8444}
     c. Compares to baseline in autoresearch/results.tsv
     d. Writes row: timestamp, commit, score, baseline, f1, KEEP/DISCARD
     e. Exits 0 (KEEP) or 1 (DISCARD)
5. KEEP:  git add SKILL.md && git commit -m "keep: score=X <description>"
6. DISCARD: git checkout -- SKILL.md
7. Repeat (NEVER STOP)
```

### The Metric

```
quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)
```

- `routing_accuracy`: fraction of `evals.json` prompts correctly routed (keyword overlap vs frontmatter)
- `heuristic_score`: structural health (has `<example>` blocks, min length)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  - The dual condition (score + f1) prevents keyword-stuffing exploits

### Baseline (2026-03-28)

| metric | value |
|---|---|
| score | 0.8444 |
| f1 | 0.8333 |
| commit | abeb626 |
| status | BASELINE |

---

## File Map: Where Everything Lives

| File | Purpose | Who touches it |
|---|---|---|
| `eval-autoresearch-fit/SKILL.md` | Assessment instructions (scoring rubric, output format) | Human / agent running assessment |
| `eval-autoresearch-fit/scripts/update_ranked_skills.py` | CLI to update summary-ranked-skills.json | eval-autoresearch-fit skill (Step 5) |
| `eval-autoresearch-fit/assets/resources/summary-ranked-skills.json` | Canonical list: all skills + their scores + status | update_ranked_skills.py |
| `<target-skill>/autoresearch/program.md` | Loop spec: goal, mutation target, locked files, NEVER STOP | Human (written once) |
| `<target-skill>/autoresearch/evaluate.py` | Locked evaluator: runs scorer, records KEEP/DISCARD | NOBODY - immutable |
| `<target-skill>/autoresearch/results.tsv` | Experiment ledger: one row per iteration | evaluate.py (appends) |
| `<target-skill>/SKILL.md` | The mutation target: agent edits this each iteration | Agent (loop body) |

---

## What "Locked" Means in Practice

The program.md specifies:
> "Locked: autoresearch/evaluate.py, evals/evals.json, scripts/eval_runner.py"

If the agent modifies evaluate.py, it can trivially make every run return KEEP (Goodhart's Law).
If the agent modifies evals.json, it can remove hard test cases.
Locking these files makes the metric trustworthy.

The agent's ONLY job: improve SKILL.md until the locked evaluator scores it higher.

---

## Connecting Back to the Assessment

`eval-autoresearch-fit` assessed `skill-improvement-eval` and scored it:

| Dimension | Score | Rationale |
|---|---|---|
| Objectivity | 7/10 | Keyword routing is deterministic; heuristic check is rule-based |
| Execution Speed | 9/10 | Runs in <5 seconds, no LLM call needed |
| Frequency of Use | 7/10 | Used whenever a skill change is proposed |
| Potential Utility | 3/10 | Scores skill routing accuracy - useful but not systemic |
| **TOTAL** | **26/40** | MEDIUM |

**Loop type: LLM_IN_LOOP** (initially assessed) - but the actual evaluator turned out to be DETERMINISTIC (pure Python keyword matching, no API calls). Reassess: this is likely 30-32/40 with a DETERMINISTIC loop type.

This is a good meta-example of the assessment process: the first pass got it slightly wrong (assumed LLM would be needed), and the actual implementation revealed it's deterministic. Re-running `eval-autoresearch-fit` on itself after building the loop is good practice.

---

## The Loop vs The Evals

These are two different things that are easy to confuse:

| | `evals/evals.json` | `autoresearch/evaluate.py` |
|---|---|---|
| **Purpose** | Tests whether the skill TRIGGERS correctly | Measures how GOOD the SKILL.md instructions are |
| **Run by** | CI / `run_eval.py` | The autoresearch loop agent |
| **Mutable** | NO (locked in loop) | NO (locked evaluator) |
| **Output** | Pass/fail per trigger scenario | A single quality_score float |

`evals.json` defines WHAT to test. `evaluate.py` uses it AS the benchmark.

---

## Summary

```
Karpathy paper
    |
    v
eval-autoresearch-fit   <-- "should we run the loop on this skill?"
    |
    | scores HIGH/MEDIUM
    v
autoresearch/ scaffolded inside target skill
    |
    +-- program.md        (the spec)
    +-- evaluate.py       (locked scorer)
    +-- results.tsv       (ledger)
    +-- symlink to eval_runner.py
    |
    v
Agent loop: edit SKILL.md -> evaluate.py -> KEEP or DISCARD -> repeat
```

The bottleneck is not running the loop. The bottleneck is `program.md`: knowing what to measure and setting the right constraints.
