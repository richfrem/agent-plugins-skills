---
name: os-lab-scorer
description: >
  Locked KEEP/DISCARD check for one change to a skill. Runs evaluate.py headlessly,
  compares accuracy and F1 against the baseline in evals/results.tsv, applies the holdout
  overfitting gate, and returns exit 0 (KEEP) or 1 (DISCARD, auto-reverted). Also runs a
  single-pass RED-GREEN-REFACTOR fix: baseline the failure, state a hypothesis, patch
  SKILL.md, require KEEP. Use when the user says "evaluate this skill", "score this change",
  "KEEP or DISCARD", "improve skill routing", "skill is not triggering", "fix skill
  description", or when os-lab-loop proposes a change that needs validation.
  DO NOT USE for the multi-iteration loop (os-lab-loop), building the lab repo
  (os-lab-setup), planning (os-lab-planner), reviewing a lab diff (os-lab-backport),
  run logs and charts (os-lab-log), or memory promotion (os-memory-manager).
  NOT for scaffolding new skills: use create-skill (agent-scaffolders).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Lab Scorer (`os-lab-scorer`)

One locked check for one change. It never loops: the loop belongs to `os-lab-loop`, which calls
this skill once per change. Two modes share the same gate: **check** (score a change someone
else proposed) and **single pass** (RED-GREEN-REFACTOR on one skill).

## Contents

- [Critical constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical constraints

1. **Locked evaluator**: never modify `evaluate.py`, `eval_runner.py` or `evals/evals.json` to make a score pass. Only the target `SKILL.md` changes.
2. **Objective verification**: never simulate routing or judge by impression. Every verdict comes from running `evaluate.py`.
3. **One variable per change**: reject bulk rewrites; the gate cannot attribute a score change to several edits.
4. **Holdout gate**: if base score rises but holdout score falls, force DISCARD (overfitting). A run with no holdout set is incomplete.
5. **F1 guard**: never disable the `f1 >= baseline_f1` check; it is the only defense against keyword stuffing.

## Quick start

Baseline a target once, then score each change:

```bash
python scripts/evaluate.py --skill <path/to/target-skill> --baseline --desc "initial baseline"
python scripts/evaluate.py --skill <path/to/target-skill> --desc "what changed"
echo $?   # 0 = KEEP, 1 = DISCARD (reverted), 2 = path error, 3 = tampered environment
```

Pass the skill folder, not a file. State lives in the target: `evals/evals.json`,
`evals/results.tsv` and its optimization program file.

## Workflow

### Mode 1: Check one change

1. Confirm the proposal changes one variable and write it to the target `SKILL.md`.
2. Run `evaluate.py`; read the exit code and the new row in `evals/results.tsv`.
3. Apply the holdout gate (see [overfitting-gate.md](references/overfitting-gate.md)).
4. DISCARD: confirm `SKILL.md` was restored and report score, delta and F1. KEEP: commit the single change (`keep: score=<s> f1=<f1> <desc>`).
5. Return the verdict to the caller. Exit codes 2 and 3 are not verdicts; see [troubleshooting.md](references/troubleshooting.md).

Steps in full: [check-protocol.md](references/check-protocol.md).

### Mode 2: Single-pass RED-GREEN-REFACTOR

Use when one skill routes badly and the user wants one focused repair, not a loop.

1. **RED**: snapshot the failure (`python scripts/eval_runner.py --skill <folder> --snapshot`) and write down the exact failing input and whether the problem is precision or recall.
2. **Hypothesis**: state failure mode, root cause, one change, expected effect and risk before touching files.
3. **GREEN**: patch the target `SKILL.md` (description, trigger phrases, examples) with that one change.
4. **Score**: run Mode 1; require KEEP.
5. **REFACTOR**: if inputs still fail, form a new hypothesis and repeat from step 2 until the target score or three consecutive DISCARDs (then hand to `os-lab-loop` or `os-lab-planner`).

Detail and templates: [red-green-refactor.md](references/red-green-refactor.md).

## Verification

```bash
python scripts/evaluate.py --skill <path/to/target-skill> --decision-only
```

`--decision-only` computes the verdict and exit code (0 KEEP or BASELINE, 1 DISCARD) without reverting files. Needs an existing baseline.

## References

- [check-protocol.md](references/check-protocol.md) - phases, revert protocol, commit format.
- [overfitting-gate.md](references/overfitting-gate.md) - holdout rule and forced DISCARD.
- [red-green-refactor.md](references/red-green-refactor.md) - hypothesis block, frontmatter and example templates, anti-patterns.
- [troubleshooting.md](references/troubleshooting.md) - exit codes, keywords footgun, 4-character word floor, re-baselining.
