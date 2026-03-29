# Optimization Program: eval-autoresearch-fit

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly routed via keyword overlap against SKILL.md frontmatter only
- `heuristic_score`: structural health check (example tags, length)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1` (dual guard prevents keyword-stuffing)

Mutation target: `SKILL.md` -- you may ONLY edit this file each iteration.

Locked (never modify):
- `plugins/agent-agentic-os/scripts/evaluate.py`
- `plugins/agent-agentic-os/scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `SKILL.md` (one focused change per iteration — frontmatter description/triggers only)
2. `python plugins/agent-agentic-os/scripts/evaluate.py --skill plugin-research/experiments/analyze-candidates-for-auto-reseaarch/skills/eval-autoresearch-fit/SKILL.md --desc "what you changed"`
3. If KEEP (exit 0): `git add SKILL.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted SKILL.md automatically

NEVER STOP. Run until manually interrupted.
