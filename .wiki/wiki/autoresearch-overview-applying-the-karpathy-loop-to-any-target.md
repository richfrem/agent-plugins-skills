---
concept: autoresearch-overview-applying-the-karpathy-loop-to-any-target
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-runner/references/autoresearch-overview.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.149039+00:00
cluster: plugin-code
content_hash: be615ce3c604c0ae
---

# Autoresearch Overview: Applying the Karpathy Loop to Any Target

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Autoresearch Overview: Applying the Karpathy Loop to Any Target

**Reference:** `references/research/karpathy-autoresearch-3-file-eval.md`
**Related research:** `references/research/meta-harness-lee-2026.md` (arXiv:2603.28052)
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
- Evaluating a skill → the skill's own directory: `.agents/skills/my-skill/`
- Evaluating a Python module → the project dir containing the module
- General experiment → a dedicated experiment folder anywhere in the repo

---

## Concrete Example: os-eval-runner (Meta-Circular Case)

> The skill evaluating itself. This is legitimate — the loop can optimize
> os-eval-runner's own SKILL.md trigger phrases.

```
<experiment-dir> = .agents/skills/os-eval-runner/
<mutation-target> = SKILL.md
```

Baseline: score=0.9100, f1=1.0000 (established 2026-03-29)

---

## How One Loop Iteration Works

```
Step 0: SETUP (run once before the loop)
  python scripts/init_autoresearch.py \
      --experiment-dir <experiment-di

*(content truncated)*

## See Also

- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[triple-loop-learning-system---architecture-overview]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[skill-optimization-guide-karpathy-loop]]
- [[overview-of-autoresearch-programmd]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-runner/references/autoresearch-overview.md`
- **Indexed:** 2026-04-17T06:42:10.149039+00:00
