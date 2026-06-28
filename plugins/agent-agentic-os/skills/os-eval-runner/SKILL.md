---
name: os-eval-runner
plugin: agent-agentic-os
description: >
  Stateless evaluation engine that scores and gates skill improvement iterations using
  headless Python evaluation scripts. Use when the user says "evaluate this skill",
  "run autoresearch loop on", "optimize this skill", "run the eval loop", or when
  another agent proposes a change and needs validation.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Skill Improvement Evaluator

Stateless evaluation engine that scores and gates skill improvement iterations using headless Python evaluation scripts.

---

## Ownership Boundary (Critical)

### What os-eval-runner owns (permanent, version-controlled with this skill)
- Scoring scripts: `./scripts/evaluate.py`, `./scripts/eval_runner.py`
- Scaffold script: `./scripts/init_autoresearch.py`
- Templates: `./assets/templates/autoresearch/` (program, evals, results, proposer prompt)

### What lives with the target (deployed per experiment)
All experiment state deploys alongside the target (e.g. `<experiment-dir>/references/program.md`, `<experiment-dir>/evals/evals.json`, `<experiment-dir>/evals/results.tsv`). You MUST read the spec from `<experiment-dir>/references/program.md` and NOT fall back to engine-local config templates.

---

## Phase 0: Intake Interview

Run this interview before starting any loop or evaluation. If enough information is provided in the initial prompt, skip the redundant questions.

1. **Q1 — What target skill are you evaluating?** (Provide path to skill folder)
2. **Q2 — Where should the experiment files live?** (Defaults to target skill directory)
3. **Q2b — What metric are you optimizing?** (quality_score, f1, precision, recall, or heuristic)
4. **Q3 — What mode?** (Loop mode for autonomous improvement vs QA mode for single diff validation)
5. **Q4 — (Loop mode) How many iterations?** (Default: NEVER STOP)
6. **Q5 — Does evals.json exist?** (If missing, scaffold from template)
7. **Q6 — Does program.md exist?** (If missing, scaffold from template)
8. **Q7 — Does a baseline score exist?** (If missing, run evaluate.py with `--baseline`)

---

## Two Modes: Summarized

- **Mode 1: Autoresearch Loop**: Autonomous iterative improvement. The agent identifies failure types, requests mutations via external proposer CLI (Copilot/Gemini), and runs the eval gate iteratively until the budget or target score is met.
- **Mode 2: Single-shot QA**: Simple gate validation. Evaluates one specific proposed diff against the baseline and decides KEEP (exit 0) or DISCARD (revert, exit 1).

---

## Stage Pointers & Reference Protocols

- [Setup: Start a New Experiment](references/quickstart-setup.md) — 4-step setup and re-baselining procedure.
- [Mode 1: Autoresearch Loop Protocol](references/mode-1-loop-protocol.md) — Proposer cycles, prompt mutations, and evaluation loop.
- [Mode 2: Single-shot QA Protocol](references/mode-2-qa-protocol.md) — Context acquisition, reverts, and reporting.
- [Phase 2b: Overfitting Gate](references/overfitting-gate.md) — Holdout set overfitting checks and forced discard logic.
- [Phase 5: Self-Assessment Survey](references/survey-protocol.md) — Mandatory evaluator survey guidelines.

---

## Smoke Test & Gotchas

### Smoke Test
1. Scaffold an experiment: `python3 ./scripts/init_autoresearch.py --experiment-dir temp/test-exp --mutation-target SKILL.md`.
2. Establish baseline: `python3 ./scripts/evaluate.py --skill temp/test-exp --baseline --desc "smoke test"`.
3. Validate exit code: Assert `results.tsv` is created, and running `evaluate.py` returns 0.

### Gotchas
- **Subjective Simulation**: Avoid "mentally simulating" routing accuracy. Subjective audits are strictly banned; run Python evaluation scripts.
- **Missing Holdout**: Starting loops without holdout prompts. This bypasses the overfitting gate, rendering the results invalid.
- **Keywords Footgun**: Adding too many triggers to frontmatter. This dilutes semantic discrimination and degrades overall router precision.
