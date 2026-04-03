# Optimization Program: os-eval-lab-setup

Goal: maximize `quality_score` (higher is better, max 1.0).
Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

Mutation target: `SKILL.md` — only this file changes each iteration.
Locked: `evals/evals.json`, `evaluate.py`, `eval_runner.py`

How to run one iteration:
```bash
python3 plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py \
  --skill plugins/agent-agentic-os/skills/os-eval-lab-setup \
  --desc "what changed"
```

NEVER STOP. Run until target score or human interruption.

## Notes
- **Optimizing**: Routing accuracy for os-eval-lab-setup — triggers on SETUP/BOOTSTRAP requests for isolated eval lab repos, NOT on running the actual eval loop or backporting results
- **Target score**: 0.95
- **Baseline**: starting fresh with formal tracking
- **Key failure modes**: Confusion with os-eval-runner (run loop) vs os-eval-backport (review results) — this skill is only for SETUP
- **Meta-circular note**: This skill sets up the very infrastructure that evaluates it. The lock on evals.json prevents the agent from gaming the metric by changing what "set up eval lab" means.
