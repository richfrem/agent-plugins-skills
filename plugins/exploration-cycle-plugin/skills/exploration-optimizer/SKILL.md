---
name: exploration-optimizer
description: Evaluates and improves the exploration-cycle skills, prompts, routing, and artifact quality using baseline-first, one-hypothesis iteration loops with keep-discard decisions and experiment ledgers.
allowed-tools: Bash, Read, Write
---

# Exploration Optimizer
[See acceptance criteria](references/acceptance-criteria.md)

## Discovery Phase
Ask for:
- The target exploration skill or agent to optimize.
- The eval set to use, or whether to generate one from the current architecture.
- The iteration budget.
- Whether auto-apply of winning variants is allowed.
- Which metrics matter most for this loop: routing quality, artifact usefulness, handoff stability, re-entry quality, or human intervention burden.
- Whether post-run survey data exists and should be included in the decision.

## Recap
Confirm:
- target component
- eval source
- loop budget
- chosen scoring dimensions
- whether survey data is available
- whether auto-apply is enabled

## Execution
This skill implements autoresearch-style optimization for the exploration-cycle system. It uses a baseline-first iteration loop to improve skill prompts and logic.

**Usage:**
```bash
python3 ${plugins}/skills/exploration-optimizer/scripts/execute.py \
  --target ${plugins}/skills/user-story-capture/SKILL.md \
  --eval-script .agents/skills/skill-improvement-eval/scripts/eval_runner.py \
  --goal "Improve Gherkin block accuracy" \
  --iterations 3
```

For a concrete target-specific playbook, use [references/spec-kitty-skill-optimizer-program.md](references/spec-kitty-skill-optimizer-program.md) when optimizing the Spec-Kitty agent/workflow files themselves.

## Iteration Loop
The `execute.py` script follows a disciplined loop:
1. Change one dominant variable per iteration.
2. Re-run evaluations.
3. Mark the attempt as `keep` or `discard`.
4. If the run crashes or times out, log the failure and continue from the last known good state.
5. Never let a subjective preference override a clear regression in the tracked metrics.
6. Use survey feedback as a quality signal, not an excuse to ignore the baseline-first method.

## Suggested Metrics

- routing quality
- artifact usefulness
- handoff stability
- re-entry usefulness
- human intervention burden
- unnecessary agent invocation rate
- post-run survey composite score

## Output
Always conclude execution with a Source Transparency Declaration explicitly listing what was queried to guarantee user trust:
**Sources Checked:** [list]
**Sources Unavailable:** [list]

## Next Actions
<!-- Suggest logical follow-up skills here. For example: -->
- Use `./scripts/benchmarking/run_loop.py --results-dir evals/experiments` for repeatable improvement loops.
- Suggest the user run `audit-plugin` to verify the generated artifacts.
