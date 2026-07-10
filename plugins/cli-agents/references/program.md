# Optimization Program: copilot-cli-agent

Goal: maximize `quality_score` (higher is better, max 1.0).
Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

Mutation target: `SKILL.md` — only this file changes each iteration.
Locked: `evals/evals.json`, `evaluate.py`, `eval_runner.py`

How to run one iteration (from within this skill's directory):
```bash
python ../os-eval-runner/scripts/evaluate.py \
  --skill . \
  --desc "what changed"
```

NEVER STOP. Run until target score or human interruption.

## Notes
- **Optimizing**: Routing accuracy for copilot-cli-agent — triggers on piping large contexts to Copilot for security/QA/architecture analysis via CLI, NOT on Copilot installation/setup tasks
- **Target score**: 0.95
- **Baseline**: untracked prior history — current state is starting point
- **Key failure modes**: Over-triggering on "install copilot", under-triggering on "pipe via shell to copilot"
- **Proposer**: Use `copilot -p "..."` as the mutation proposer once baseline is established
