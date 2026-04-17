---
concept: autoresearch-architecture
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-runner/references/autoresearch-architecture.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.148590+00:00
cluster: skill
content_hash: 651a6d2f042d8cb6
---

# Autoresearch Architecture

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Autoresearch Architecture

**Reference:** `references/research/karpathy-autoresearch-3-file-eval.md`
**Sequence Diagram:** `references/diagrams/autoresearch-loop.mmd`
**Mapping Diagram:** `references/diagrams/mapping-karpathy-to-os-eval-runner.mmd`

---

## Purpose

`os-eval-runner` is a general-purpose evaluation SERVICE. It can run the
Karpathy autoresearch loop against ANY target — a SKILL.md, a Python script, a
config file, anything with a measurable output. The scripts and templates live here.
All experiment state lives with each target.

---

## Two Layers: Templates vs Deployed Copies

This is the most important concept to understand before using this system.

```
os-eval-runner/          <-- THE EVALUATOR (stateless service)
  scripts/                       scripts run here, never move
  assets/templates/autoresearch/ MASTER templates — never edit directly
    program.md.template
    evals.json.template
    results.tsv.template

your-experiment-dir/             <-- THE EXPERIMENT (lives with the target)
  <mutation-target>              the file being mutated (SKILL.md, .py, etc.)
  references/program.md          COPY of program.md.template, filled in for this experiment
  evals/evals.json               COPY of evals.json.template, filled in with real test prompts
  evals/results.tsv              COPY of results.tsv.template header, then appended by evaluate.py
  evals/.lock.hashes             SHA256 snapshot written by evaluate.py --baseline
```

`init_autoresearch.py` does the copy step: reads templates, renders `{{PLACEHOLDERS}}`,
writes rendered files into the experiment directory.

---

## Karpathy 3-Component Mapping

In Karpathy's original ML pattern:
- `train.py` is the mutation target — the script being optimized
- `prepare.py` is the locked evaluator — scores the mutation target
- The **agent** is the loop orchestrator — reads program.md, edits train.py, runs prepare.py, decides KEEP/DISCARD, repeats

There is no separate orchestrator script. The agent IS the loop.

| Karpathy Original | Our Implementation | File | Location |
|---|---|---|---|
| `program.md` | `program.md` | Spec: optimization goal, locked files, NEVER STOP | `<experiment-dir>/references/program.md` (deployed from template) |
| `train.py` | any file | **Mutation target** — the only file the agent changes each iteration | `<experiment-dir>/<mutation-target>` (SKILL.md, .py, etc.) |
| _(input to prepare.py)_ | `evals.json` | Test prompts with expected outcomes | `<experiment-dir>/evals/evals.json` (deployed from template) |
| `prepare.py` | `eval_runner.py` | **Metric producer** — reads target + evals.json, outputs metrics JSON | `os-eval-runner/scripts/eval_runner.py` |
| `prepare.py` (gate logic) | `evaluate.py` | **Loop gate** — calls runner, reads baseline, writes ledger row, exits 0/1 | `os-eval-runner/scripts/evaluate.py` |
| `results.tsv` | `results.tsv` | Scoring history for this experiment | `<experiment-dir>/evals/results.tsv` (deployed from template, appended by evaluate.py) |
| The agent | The agent | Loop orchestrator — reads program.md, edits target, handles KEEP/DISCARD, loops forever | _(agent following program.md)_ |

---

## New: Scaffold Layer (no Karpathy equivalent)

Karpathy's original assumed you hand-wrote program.md and prepared evals manually.
We added a scaffold layer to standardize this:

| Component | Role | Location |
|---|---|---|
| `program.md.template` | Master spec template with `{{PLACEHOLDERS}}` | `os-eval-runner/assets/templates/autoresearch/` |
| `evals.json.template` | Master evals template with placeholder prompts | `os-eval-runner/assets/templates/autoresearch/` |
| `results.tsv.template` | TSV schema header (column names only) | `os-eval-runner/assets/templates/autoresearch/` |
| `init_autoresearch.py` | Renders and deploys all three templates to the experiment dir | `os-eval-runner/scripts/` |

**How to use:**
```bash
# Deploy templates into a new experiment
python ./scripts/init_autoresearch.py \
   

*(content truncated)*

## See Also

- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[triple-loop-learning-system---architecture-overview]]
- [[agentic-os-architecture]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-runner/references/autoresearch-architecture.md`
- **Indexed:** 2026-04-17T06:42:10.148590+00:00
