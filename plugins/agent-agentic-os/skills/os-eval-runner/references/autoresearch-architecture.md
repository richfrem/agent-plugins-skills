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
    --experiment-dir <path/to/experiment> \
    --mutation-target SKILL.md   # or any filename
```

---

## Why eval_runner.py and evaluate.py Are Both Needed

`prepare.py` in Karpathy's original does two things: produces the metric AND makes
the KEEP/DISCARD decision. We split this because `eval_runner.py` is general-purpose
— it can score any target standalone, outside any loop context.

| Script | Single responsibility | Usable outside loop |
|---|---|---|
| `eval_runner.py` | "What is the score of this target file?" | YES |
| `evaluate.py` | "Should the loop keep or discard this change?" | NO |

---

## Summary: Who Owns What

| Owner | Files | Purpose |
|---|---|---|
| **os-eval-runner** | `scripts/eval_runner.py` | Metric producer |
| **os-eval-runner** | `scripts/evaluate.py` | Loop gate |
| **os-eval-runner** | `scripts/init_autoresearch.py` | Scaffold deployer |
| **os-eval-runner** | `assets/templates/autoresearch/*.template` | Master templates |
| **Each experiment** | `<mutation-target>` | What is being optimized |
| **Each experiment** | `evals/evals.json` | Test prompts (deployed from template, locked during loop) |
| **Each experiment** | `evals/results.tsv` | Scoring history (deployed from template, appended by evaluate.py) |
| **Each experiment** | `evals/.lock.hashes` | SHA256 snapshot of locked files at baseline |
| **Each experiment** | `references/program.md` | Loop spec (deployed from template) |

---

## results.tsv Schema

Lives at `<experiment-dir>/evals/results.tsv`.

| Column | Description |
|---|---|
| `timestamp` | ISO datetime of the run |
| `commit` | git short hash at time of run |
| `score` | final quality_score (0.0 - 1.0) |
| `baseline` | baseline score loaded from last BASELINE row |
| `accuracy` | routing accuracy component |
| `heuristic` | structural health component |
| `f1` | F1 score (prevents keyword-stuffing exploit) |
| `status` | BASELINE / KEEP / DISCARD |
| `description` | what was changed this iteration |

---

## v3 Changes (Fixed)

| Item | v2 State | v3 Fix |
|---|---|---|
| `eval_runner.py` scope | Scored a single SKILL.md file | Scores the entire skill folder (SKILL.md + scripts/ + references/) |
| Heuristic spec | Internal convention only (`<example>` tags + length) | Enforces agentskills.io spec: name format, description length, folder-name match, scripts py_compile, empty reference check |
| Hard fail rules | Frontmatter malformed | Frontmatter malformed + name invalid + description empty — all return score=0.0 |
| DISCARD revert scope | `git checkout -- SKILL.md` (single file) | `git checkout -- .` from skill_root (entire folder) |
| evaluate.py `--skill` | Required SKILL.md file path | Accepts skill folder path (primary) OR any file within the skill (backward compat) |

## v2 Changes (Fixed)

| Item | v1 Bug | v2 Fix |
|---|---|---|
| `eval_runner.py` purity | Wrote to TSV on every call | Pure scorer — writes nothing; `--json` outputs all four metric fields |
| `evaluate.py` baseline read | Read first BASELINE row (f1=0.0 corrupted F1 guard) | Reads last BASELINE row; F1 guard active |
| `evaluate.py` double call | Called eval_runner twice per iteration | Single call |
| `evaluate.py` lock enforcement | Convention only (program.md) | Runtime `git status` check at startup, plus SHA256 hash snapshot at baseline |
| `evaluate.py` DISCARD revert | Agent responsible for `git checkout` (unreliable) | `evaluate.py` runs `git checkout -- <target>` before `sys.exit(1)` |
| `evaluate.py` frontmatter fallback | Fell back to full file body if frontmatter malformed | Hard fail — returns accuracy=0.0 if frontmatter missing or malformed |
| Float precision | `0.9099999999999999 < 0.91` caused false DISCARD at ceiling | Comparison uses `round(score, 4) >= round(baseline, 4)` |
| Ledger location | Single central `autoresearch/results.tsv` | One per experiment: `<experiment-dir>/evals/results.tsv` |
| Scaffold | No tooling — hand-write program.md | `init_autoresearch.py` deploys all 3 templates into experiment dir |

## Known Risks (Remaining)

| Risk | Severity | Description |
|---|---|---|
| Meta-circular risk | Medium | This skill is used to improve itself. The lock check and hash snapshot reduce this but cannot fully prevent an agent from modifying non-target files in clever ways. |
| Keyword-overlap is a proxy | Medium | The metric measures keyword overlap, not actual agent routing. A high score does not guarantee correct production routing. |
| SHA256 scope | Low | Hash check detects modified-then-committed locked files, but a committed-then-restored attack (modify -> commit -> restore -> commit) still passes. |
| Heuristic is skill-folder specific | Low | `calculate_heuristic_score()` follows the agentskills.io spec (YAML frontmatter, name/description rules, `<example>` tags, scripts/ py_compile). If the mutation target is not an agent skill folder, these checks will produce low or 0.0 heuristic scores. The architectural path for non-skill targets is a per-experiment `eval_runner.py` template. |
| REPLACE placeholder risk | High | `init_autoresearch.py` scaffolds `evals.json` with placeholder prompts. If the operator does not replace them before `--baseline`, the evaluator will score keyword overlap against "REPLACE", producing a meaningless baseline. There is no runtime check that placeholders have been filled. |
