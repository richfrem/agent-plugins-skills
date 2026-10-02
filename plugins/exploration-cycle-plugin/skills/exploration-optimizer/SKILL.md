---
name: exploration-optimizer
plugin: exploration-cycle-plugin
description: Evaluates and improves the exploration-cycle skills, prompts, routing, and artifact quality using baseline-first, one-hypothesis iteration loops with keep-discard decisions and experiment ledgers.
allowed-tools: Bash, Read, Write
---

# Exploration Optimizer (`exploration-optimizer`)

Evaluates and optimizes exploration-cycle skills and prompts using disciplined, baseline-first iteration loops.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **One-hypothesis discipline**: Change exactly one variable per iteration loop.
- **Programmatic baselines**: Acceptance requires automated benchmark score improvement over baseline.
- **Fail-safe revert**: Automatically discard regressions; retain only verified improvements.

## Quick start

```bash
# Execute optimization loop on target skill
python ./scripts/execute.py \
  --target plugins/exploration-cycle-plugin/skills/<skill>/SKILL.md \
  --eval-script ./scripts/eval_runner.py \
  --goal "Improve routing precision" \
  --iterations 3
```

## Workflow

1. **Configuration**: Confirm target skill, evaluation benchmark script, and iteration budget.
2. **Baseline Run**: Establish baseline score using deterministic evaluation fixtures.
3. **Mutation**: Mutate one hypothesis at a time in isolated worktree.
4. **Scoring**: Re-evaluate against the baseline. Keep wins, discard regressions.
5. **Ledger Declaration**: Conclude with Source Transparency Declaration and iteration ledger.

## Verification

```bash
# Verify evaluation fixtures run cleanly
pytest plugins/exploration-cycle-plugin/tests/
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for exploration optimization loops.
- [dispatch-strategies.md](references/dispatch-strategies.md) — Model dispatching and evaluation strategies.
