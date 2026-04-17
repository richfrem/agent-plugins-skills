---
concept: optimization-program-os-improvement-loop
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-improvement-loop/references/program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.164760+00:00
cluster: target
content_hash: a7f5e8cbc4643ea0
---

# Optimization Program: os-improvement-loop

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Optimization Program: os-improvement-loop

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly matched against
  the mutation target's frontmatter content
- `heuristic_score`: structural health check (description length, example blocks, trigger coverage)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1`
  (dual guard prevents metric gaming: padding increases recall but drops precision/F1)

Mutation target: `SKILL.md` — you may ONLY edit this file each iteration.
One focused change per iteration. No bulk rewrites.

Locked (never modify during the loop):
- `scripts/evaluate.py`
- `scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `SKILL.md` (one focused change to description, triggers, or examples)
2. `python scripts/evaluate.py --skill . --desc "what you changed"`
3. If KEEP (exit 0): `git add SKILL.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted `SKILL.md` automatically

NEVER STOP. Run until manually interrupted or target score is reached.

---

## Notes

- **What is being optimized**: Routing accuracy — ensuring os-improvement-loop triggers on
  concurrent multi-agent coordination requests and NOT on single-agent tasks like learning-loop,
  eval-runner, or memory-manager (which share some vocabulary)
- **Target score**: 0.90
- **Max iterations**: 30
- **Baseline established**: <!-- filled in by evaluate.py --baseline -->
- **Key adversarial risk**: "run the learning loop", "evaluate this skill", "write a memory log"
  share vocabulary with this skill's description but should NOT trigger it


## See Also

- [[optimization-program-os-eval-lab-setup]]
- [[optimization-program-os-eval-runner]]
- [[optimization-program-os-eval-lab-setup]]
- [[optimization-program-os-eval-runner]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[os-loop-command]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-improvement-loop/references/program.md`
- **Indexed:** 2026-04-17T06:42:10.164760+00:00
