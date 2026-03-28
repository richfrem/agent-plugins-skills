# Optimization Program: skill-improvement-eval

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly routed via keyword overlap
- `heuristic_score`: structural health check (example tags, length)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`

Mutation target: `../SKILL.md` -- you may ONLY edit this file each iteration.

Locked (never modify):
- `autoresearch/evaluate.py`
- `scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `../SKILL.md` (one focused change per iteration)
2. `python autoresearch/evaluate.py --desc "what you changed"`
3. If KEEP: `git add ../SKILL.md && git commit -m "keep: score=X <description>"`
4. If DISCARD: `git checkout -- ../SKILL.md`

NEVER STOP. Run until manually interrupted.
