---
name: os-skill-improvement
version: 1.0.0
description: >
  Continuously improves an existing agent skill based on eval results using the
  RED-GREEN-REFACTOR cycle. Apply when a skill's routing accuracy is low, trigger
  descriptions need sharpening, or os-eval-runner scores are below target.
  (1) run a RED baseline to observe the failure mode,
  (2) apply a focused patch and verify with os-eval-runner (GREEN),
  (3) refactor to close loopholes until score meets threshold.
  Integrates with os-eval-runner as the objective eval gate.
  NOT for scaffolding new skills — use create-skill (agent-scaffolders) for that.
trigger: improve a skill, improve skill routing, fix routing accuracy, skill is not triggering,
  skill triggers too often, improve trigger description, update a skill trigger, skill patch,
  improve triggers, route a skill, routing precision, fix skill description, skill scoring low,
  eval score low, skill improvement, continuous skill improvement, refactor skill triggers,
  tdd for documentation, skill not routing correctly
allowed-tools: Read, Write, Edit, Bash
---

# Skill Improvement: RED-GREEN-REFACTOR (`os-skill-improvement`)

Adapts the RED-GREEN-REFACTOR cycle from software testing to skill authoring. A skill is a testable contract: always observe the failure BEFORE writing the fix.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Observe Failure First**: Never patch a skill without first running a RED scenario to observe empirical failure.
2. **Objective Eval Gate**: Every patch must be scored by `eval_runner.py` and achieve a KEEP verdict.
3. **No Scaffolding**: Use `create-skill` for scaffolding new skills; this skill only optimizes existing skills.

## Quick start

Snapshot the current skill evaluation baseline:

```bash
python3 scripts/eval_runner.py --skill <path/to/skill> --snapshot
```

## Workflow

1. **Observe RED Baseline**: Run pressure scenario without patch; document baseline failure mode.
2. **Declare Hypothesis**: State expected routing gain or precision fix before modifying files.
3. **GREEN Patch**: Edit `SKILL.md` description, trigger keywords, and representative examples.
4. **Evaluate**: Run `python3 scripts/eval_runner.py --skill <dir>`; require KEEP verdict.
5. **REFACTOR**: Close remaining edge cases and loopholes revealed by eval failures.

## Verification

Confirm skill passes evaluation with improved or equal score:

```bash
python3 scripts/eval_runner.py --skill <path/to/skill> --decision-only
```

## References

- [detailed-reference.md](references/detailed-reference.md) — TDD mapping, pressure scenarios, and baseline protocols.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for continuous skill improvement.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways when refactoring fails to converge.
- [skill_optimization_guide.md](references/operations/skill_optimization_guide.md) — Routing accuracy patterns and heuristics.
- [test-registry-protocol.md](references/testing/test-registry-protocol.md) — Test scenario registration standards.
