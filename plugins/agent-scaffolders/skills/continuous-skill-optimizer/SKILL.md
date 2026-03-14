---
name: continuous-skill-optimizer
description: Autonomous optimization loop for any skill. Runs baseline-first evaluation, performs one-hypothesis iterations, keeps only measurable improvements, logs crashes/timeouts, and preserves a persistent experiment ledger.
disable-model-invocation: false
---

# Continuous Skill Optimizer
[See acceptance criteria](references/acceptance-criteria.md)

## Discovery Phase
Ask for:
- Target skill path to optimize.
- Eval set path (or whether to use a generated default set).
- Loop budget (`max-iterations`) and aggressiveness (`runs-per-query`, `holdout`).
- Improvement backend (`claude` or `copilot`) and model choice.

## Recap
Confirm:
- Target skill path
- Eval set path
- Engines/models
- Iteration budget
- Whether auto-apply of winning description is enabled

## Execution
This skill implements autoresearch-style optimization for skill trigger quality. Use a strict loop:
1. Run one baseline evaluation and record it.
2. Change one dominant variable per iteration (usually description wording scope/specificity/exclusions).
3. Classify each iteration as `keep`, `discard`, or `crash`.
4. If an iteration crashes/timeouts, log failure and continue from last known good description.
5. Keep a persistent ledger in `evals/results.tsv`.

**Usage:**
```bash
python3 ${plugins}/skills/continuous-skill-optimizer/scripts/execute.py --help
```

## Baseline Validation
Before optimizing behavior, run one baseline evaluation and log it in `evals/results.tsv`.

## Iteration Loop
When iterating, follow a disciplined loop:
1. Change one dominant variable per iteration.
2. Re-run evaluations.
3. Mark the attempt as `keep` or `discard`.
4. If the run crashes or times out, log the failure and continue from the last known good state.
5. Never overwrite the source skill unless explicitly configured to auto-apply winners.

## Output
Always conclude execution with a Source Transparency Declaration explicitly listing what was queried to guarantee user trust:
**Sources Checked:** [list]
**Sources Unavailable:** [list]

## Next Actions
- Use `./scripts/benchmarking/run_loop.py --results-dir evals/experiments` for repeatable improvement loops.
- Use `./scripts/eval-viewer/generate_review.py` for visual review of iteration outcomes.
- Suggest the user run `audit-plugin` to verify the generated artifacts.
