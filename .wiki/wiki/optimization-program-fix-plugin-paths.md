---
concept: optimization-program-fix-plugin-paths
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/fix-plugin-paths/references/program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.091298+00:00
cluster: target
content_hash: 60785d59bc390a9c
---

# Optimization Program: fix-plugin-paths

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Optimization Program: fix-plugin-paths

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly matched against
  the mutation target's content (frontmatter + description keywords).
- `heuristic_score`: structural health check (example blocks, name format, description length).
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  (dual guard prevents metric gaming: padding increases recall but drops precision/F1)

Mutation target: `SKILL.md` — you may ONLY edit this file each iteration.
One focused change per iteration. No bulk rewrites.

Locked (never modify during the loop):
- `plugins/agent-agentic-os/scripts/evaluate.py`
- `plugins/agent-agentic-os/scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `SKILL.md` (one focused change)
2. `python3 plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py --skill plugins/agent-plugin-analyzer/skills/fix-plugin-paths --desc "what you changed"`
3. If KEEP (exit 0): `git add SKILL.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted `SKILL.md` automatically

NEVER STOP. Run until manually interrupted or target score is reached.

---

## Notes

- **What is being optimized**: Routing accuracy and structural quality of the `fix-plugin-paths` portability enforcer skill. The skill must trigger on all portability audit, path-fixing, and plugin distribution preparation requests, while NOT triggering on unrelated plugin management, creation, or formatting tasks.
- **Target score**: 0.95
- **Max iterations**: NEVER STOP — run until target OR human interruption
- **Baseline established**: <!-- date + commit hash, filled in by evaluate.py --baseline -->
- **Key failure modes**:
  - Over-triggering on general "plugin" tasks (false positives)
  - Under-triggering on "portability", "distribution", "standardize paths" phrasing (false negatives)
  - Heuristic penalties for missing `<example>` blocks or insufficient description length


## See Also

- [[optimization-program-exploration-cycle-plugin]]
- [[optimization-program-os-eval-lab-setup]]
- [[optimization-program-os-eval-runner]]
- [[optimization-program-os-improvement-loop]]
- [[optimization-program-eval-autoresearch-fit]]
- [[plugin-path-portability-fix-ruleset]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/fix-plugin-paths/references/program.md`
- **Indexed:** 2026-04-17T06:42:10.091298+00:00
