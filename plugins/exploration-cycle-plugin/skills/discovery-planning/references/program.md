# Optimization Program: discovery-planning

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly matched against
  the mutation target's content (frontmatter only for SKILL.md; full content otherwise)
- `heuristic_score`: structural health check (varies by target type)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  (dual guard prevents metric gaming: padding increases recall but drops precision/F1)

Mutation target: `SKILL.md` — you may ONLY edit this file each iteration.
One focused change per iteration. No bulk rewrites.

Locked (never modify during the loop):
- `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py`
- `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner/scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `SKILL.md` (one focused change)
2. `python /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py --skill /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/exploration-cycle-plugin/skills/discovery-planning/SKILL.md --desc "what you changed"`
3. If KEEP (exit 0): `git add SKILL.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted `SKILL.md` automatically

NEVER STOP. Run until manually interrupted or target score is reached.

---

## Notes (fill in before starting the loop)

- **What is being optimized**: <!-- e.g. skill trigger phrase coverage, function accuracy, config tuning -->
- **Target score**: <!-- e.g. 0.95, or leave blank for NEVER STOP -->
- **Max iterations**: <!-- e.g. 50, or leave blank for NEVER STOP -->
- **Baseline established**: <!-- date + commit hash, filled in by evaluate.py --baseline -->
