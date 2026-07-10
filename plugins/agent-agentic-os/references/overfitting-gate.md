# Phase 2b: Overfitting Gate

After `evaluate.py` completes, read the scores from `evals/results.tsv` for the current
iteration AND the previous baseline row. Apply this rule:

```
IF base_score > prev_base AND holdout_score < prev_holdout → OVERFIT → force DISCARD
```

This gate overrides any KEEP decision from `evaluate.py`. Overfitting is always a DISCARD
regardless of how the lab was configured. The holdout set is a **required** input — a run
without a holdout set cannot pass the overfitting gate and must be flagged as incomplete.

## Pseudocode for the overfitting check

```python
if base_score > prev_base and holdout_score < prev_holdout:
    print(f"OVERFIT DETECTED: base={base_score:.3f} (+{base_score - prev_base:.3f}) "
          f"holdout={holdout_score:.3f} ({holdout_score - prev_holdout:.3f})")
    print("Forcing DISCARD — overfitting always overrides KEEP.")
    # Treat as DISCARD: revert SKILL.md and report failure
    exit_code = 1
```

Report the overfitting event to the orchestrator with both base and holdout deltas so the
pattern is visible in the experiment log.
