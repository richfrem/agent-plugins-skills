---
concept: optimization-program-exploration-cycle-plugin
source: plugin-code
source_file: exploration-cycle-plugin/references/program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.585434+00:00
cluster: target
content_hash: 1a3cea1191aca46f
---

# Optimization Program: exploration-cycle-plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Optimization Program: exploration-cycle-plugin

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly matched against
  the mutation target's content (frontmatter only for SKILL.md; full content otherwise)
- `heuristic_score`: structural health check (varies by target type)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  (dual guard prevents metric gaming: padding increases recall but drops precision/F1)

Mutation target: `OVERVIEW.md` — you may ONLY edit this file each iteration.
One focused change per iteration. No bulk rewrites.

Locked (never modify during the loop):
- `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py`
- `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner/scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `OVERVIEW.md` (one focused change)
2. `python /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py --skill /Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/exploration-cycle-plugin/OVERVIEW.md --desc "what you changed"`
3. If KEEP (exit 0): `git add OVERVIEW.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted `OVERVIEW.md` automatically

Run iteratively. Stop when the target score is reached or when manually interrupted.

---

## Notes (fill in before starting the loop)

- **What is being optimized**: <!-- e.g. skill trigger phrase coverage, function accuracy, config tuning -->
- **Target score**: <!-- e.g. 0.95, or leave blank to run until manually interrupted -->
- **Max iterations**: <!-- e.g. 50, or leave blank to run until manually interrupted -->
- **Baseline established**: <!-- date + commit hash, filled in by evaluate.py --baseline -->


## See Also

- [[optimization-program-fix-plugin-paths]]
- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]
- [[exploration-cycle-plugin-design-recommendation]]
- [[exploration-cycle-plugin-upgrade-implementation-plan]]
- [[exploration-cycle-plugin-architecture-reference]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/references/program.md`
- **Indexed:** 2026-04-17T06:42:09.585434+00:00
