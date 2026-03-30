# Autoresearch Overview: Applying the Karpathy Loop to Any Target

**Reference:** `references/research/karpathy-autoresearch-3-file-eval.md`
**Architecture:** `references/autoresearch-architecture.md`
**Sequence Diagram:** `references/diagrams/autoresearch-loop.mmd`
**Mapping Diagram:** `references/diagrams/mapping-karpathy-to-os-eval-runner.mmd`

---

## The Big Picture

Karpathy's autoresearch pattern says: if you have a single objective metric, an
automated evaluator, and one mutable file, you can run an autonomous overnight loop
to optimize anything.

This system applies that pattern to any target — a skill definition, a Python module,
a config, a scoring function. The evaluator scripts live in `os-eval-runner`.
All experiment state (spec, test prompts, history) deploys into the target's own directory.

---

## Two Layers

### Layer 1: Assessment (eval-autoresearch-fit)

A one-time scoring pass that answers: "Is this target worth running through the loop?"
Scores each candidate 0-40 across four dimensions and outputs HIGH / MEDIUM / LOW / NOT_VIABLE.
This does NOT run the loop — it decides whether a loop is worth building.

### Layer 2: The Loop (scaffolded inside the target)

The actual autonomous optimization loop, scaffolded once you decide to proceed.

---

## Template vs Deployed Copy

The evaluator owns three master templates. You NEVER edit templates directly.
`init_autoresearch.py` reads them, fills in `{{PLACEHOLDERS}}`, and writes rendered
copies into your experiment directory.

```
TEMPLATES (master, in os-eval-runner — never edit)
  assets/templates/autoresearch/program.md.template
  assets/templates/autoresearch/evals.json.template
  assets/templates/autoresearch/results.tsv.template
        |
        |  init_autoresearch.py --experiment-dir <path> --mutation-target <file>
        v
DEPLOYED COPIES (in your experiment dir — edit these)
  <experiment-dir>/references/program.md    <-- fill in Notes section
  <experiment-dir>/evals/evals.json         <-- replace REPLACE placeholders
  <experiment-dir>/evals/results.tsv        <-- header only; evaluate.py appends rows
  <experiment-dir>/evals/.lock.hashes       <-- written by evaluate.py --baseline
```

---

## Directory Layout (Generic)

```
os-eval-runner/                      THE EVALUATOR
  scripts/
    evaluate.py                              Loop gate (locked)
    eval_runner.py                           Pure scorer (locked)
    init_autoresearch.py                     Template deployer
  assets/templates/autoresearch/             Master templates
    program.md.template
    evals.json.template
    results.tsv.template

<experiment-dir>/                            YOUR EXPERIMENT
  <mutation-target>                          The file mutated each iteration
  references/
    program.md                               Spec: goal, locked files, NEVER STOP
  evals/
    evals.json                               Test prompts (locked during loop)
    results.tsv                              Loop ledger (one row per iteration)
    .lock.hashes                             SHA256 snapshot of locked files at baseline
```

**Examples of `<experiment-dir>` for different target types:**
- Evaluating a skill → the skill's own directory: `plugins/my-plugin/skills/my-skill/`
- Evaluating a Python module → the project dir containing the module
- General experiment → a dedicated experiment folder anywhere in the repo

---

## Concrete Example: os-eval-runner (Meta-Circular Case)

> The skill evaluating itself. This is legitimate — the loop can optimize
> os-eval-runner's own SKILL.md trigger phrases.

```
<experiment-dir> = plugins/autoresearch-improvement/skills/os-eval-runner/
<mutation-target> = SKILL.md
```

Baseline: score=0.9100, f1=1.0000 (established 2026-03-29)

---

## How One Loop Iteration Works

```
Step 0: SETUP (run once before the loop)
  python scripts/init_autoresearch.py \
      --experiment-dir <experiment-dir> \
      --mutation-target <filename>
  # Edit references/program.md (goal, target score)
  # Edit evals/evals.json (real test prompts)
  python scripts/evaluate.py --skill <experiment-dir>/<target> --baseline

Step 1: Agent reads <experiment-dir>/references/program.md
        (goal, locked files, NEVER STOP)

Step 2: Agent edits <mutation-target> (ONE focused change per iteration)

Step 3: Agent runs evaluate.py:
        python scripts/evaluate.py \
            --skill <experiment-dir>/<mutation-target> \
            --desc "what I changed"

Step 4: evaluate.py internally:
        a. check_locked_files()    -- abort if locked files dirty (git status)
        b. check_sha256_hashes()   -- abort if locked files changed since baseline
        c. eval_runner.py --json   -- score: {quality_score, accuracy, f1, heuristic}
        d. load_baseline()         -- last BASELINE row from results.tsv
        e. compare score AND f1    -- dual guard prevents keyword-stuffing
        f. write row to results.tsv
        g. if KEEP: exit 0  |  if DISCARD: git checkout -- <target>, exit 1

Step 5: KEEP  -> agent: git add <target> && git commit -m "keep: score=X <desc>"
        DISCARD -> evaluate.py already reverted; agent reports score delta

Step 6: Repeat (NEVER STOP)
```

---

## The Metric

```
quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)
```

- `routing_accuracy`: fraction of `evals.json` prompts correctly matched against the
  target's frontmatter keywords. Non-SKILL.md targets (no frontmatter) return
  accuracy=0.0 — only heuristic_score contributes to quality_score for those targets.
- `heuristic_score`: structural health check (varies by target type)
- KEEP requires: `round(score, 4) >= round(baseline, 4) AND round(f1, 4) >= round(baseline_f1, 4)`
  - Dual condition prevents keyword-stuffing (padding raises recall but drops F1)
  - Round-to-4dp prevents false DISCARD from floating-point precision

---

## File Roles (Generic)

| File | Role | Who touches it |
|---|---|---|
| `assets/templates/autoresearch/*.template` | Master templates — never edited directly | `init_autoresearch.py` reads; human never edits |
| `<experiment-dir>/references/program.md` | Loop spec — goal, locked files, NEVER STOP | Human fills in after deploy; agent reads |
| `<experiment-dir>/<mutation-target>` | The file being optimized | Agent edits (one change per iteration) |
| `<experiment-dir>/evals/evals.json` | Test prompts (locked during loop) | Human fills in after deploy; nobody during loop |
| `<experiment-dir>/evals/results.tsv` | Loop ledger — one row per iteration | `evaluate.py` appends |
| `<experiment-dir>/evals/.lock.hashes` | SHA256 snapshot of locked files | `evaluate.py --baseline` writes; `evaluate.py` reads each run |
| `scripts/eval_runner.py` | Pure scorer: reads target + evals.json, outputs metrics | `evaluate.py` calls; nobody else |
| `scripts/evaluate.py` | Loop gate: calls scorer, reads baseline, writes ledger, exits 0/1 | Agent calls; nobody modifies |
| `scripts/init_autoresearch.py` | Template deployer: renders + copies templates to experiment dir | Human runs once before loop |

---

## Summary

```
Karpathy autoresearch pattern
    |
    v
eval-autoresearch-fit skill        <- "is this target worth looping on?"
    | scores HIGH or MEDIUM
    v
Setup: init_autoresearch.py
    |
    +-- <experiment-dir>/references/program.md    (rendered from template)
    +-- <experiment-dir>/evals/evals.json         (rendered from template, fill in prompts)
    +-- <experiment-dir>/evals/results.tsv        (schema header from template)
    |
    v
Baseline: evaluate.py --baseline   <- establishes score anchor + writes .lock.hashes
    |
    v
Agent loop:
    read program.md
    -> edit <mutation-target>
    -> python evaluate.py --skill <experiment-dir>/<mutation-target>
    -> KEEP: git commit | DISCARD: evaluate.py reverts automatically
    -> repeat forever

Templates stay in os-eval-runner/assets/templates/ — untouched.
All experiment state lives in <experiment-dir> — isolated per target.
```
