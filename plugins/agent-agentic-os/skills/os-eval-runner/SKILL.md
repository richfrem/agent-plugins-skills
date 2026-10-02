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

# Skill Improvement Evaluator (`os-eval-runner`)

Stateless evaluation engine that scores and gates skill improvement iterations using headless Python evaluation scripts.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Ownership Boundary**: Engine owns scripts (`evaluate.py`, `eval_runner.py`) and templates. Experiment state (`references/program.md`, `evals/evals.json`, `evals/results.tsv`) deploys strictly alongside target.
2. **Objective Verification Invariant**: Never mentally simulate routing or score subjective impressions. All evaluations must be executed programmatically via headless python scripts.
3. **Holdout & Overfitting Gate**: Loops require a locked holdout prompt set. If holdout score drops, the candidate mutation must be forcefully discarded.

## Quick start

Establish an initial baseline evaluation for a target skill:

```bash
python3 scripts/evaluate.py --skill <path/to/skill> --baseline --desc "initial baseline"
```

## Workflow

1. **Intake & Discovery**: Confirm target skill path, metric to optimize (`quality_score`, `f1`, etc.), and operating mode (Mode 1: Autoresearch Loop vs Mode 2: Single-shot QA).
2. **Scaffold Experiment State**: Ensure `evals.json` and `program.md` exist alongside target; scaffold via `scripts/init_autoresearch.py` if missing.
3. **Execution Mode**:
   - **Mode 1 (Autoresearch Loop)**: Iteratively request mutations via proposer, run `evaluate.py`, and keep or discard based on score deltas.
   - **Mode 2 (Single-shot QA)**: Evaluate proposed candidate against baseline to decide KEEP (`exit 0`) or DISCARD (`exit 1`, revert).
4. **Overfitting Check**: Run holdout set evaluation before accepting any candidate improvement.

## Verification

Execute an end-to-end smoke test verifying script execution and exit codes:

```bash
python3 scripts/init_autoresearch.py --experiment-dir temp/test-exp --mutation-target SKILL.md
python3 scripts/evaluate.py --skill temp/test-exp --baseline --desc "smoke test"
```

## References

- [quickstart-setup.md](references/quickstart-setup.md) — 4-step setup and re-baselining procedure.
- [mode-1-loop-protocol.md](references/mode-1-loop-protocol.md) — Autoresearch loop protocol and mutation cycles.
- [mode-2-qa-protocol.md](references/mode-2-qa-protocol.md) — Single-shot QA diff validation.
- [overfitting-gate.md](references/overfitting-gate.md) — Holdout set checks and forced discard logic.
- [cheapest_models.md](references/cheapest_models.md) — Recommended lightweight models for evaluation runs.
- [post_run_survey.md](references/memory/post_run_survey.md) — Mandatory post-run survey template.
- [survey-protocol.md](references/survey-protocol.md) — Evaluator survey and retrospective guidelines.
