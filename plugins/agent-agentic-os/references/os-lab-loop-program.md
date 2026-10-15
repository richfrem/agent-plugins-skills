# Optimization Program: <target-skill>  (example)

Goal: maximize `quality_score` (higher is better, max 1.0).
Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

Mutation target: `SKILL.md` — only this file changes each iteration.
Locked: `evals/evals.json`, `evaluate.py`, `eval_runner.py`

How to run one iteration (from within this skill's directory):
```bash
Invoke `os-lab-scorer` on the target folder with a one-line description of the change.
```

NEVER STOP. Run until target score or human interruption.

## Notes
- **Optimizing**: routing accuracy for the target skill
- **Target score**: 0.95
- **Baseline**: from `evals/results.tsv`
- **Key failure modes**: name the sibling skills the target is confused with
