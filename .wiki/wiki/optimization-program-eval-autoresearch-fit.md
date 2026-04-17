---
concept: optimization-program-eval-autoresearch-fit
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/eval-autoresearch-fit/references/program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.074460+00:00
cluster: only
content_hash: 5b957f4ceb9b4d02
---

# Optimization Program: eval-autoresearch-fit

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Optimization Program: eval-autoresearch-fit

Goal: maximize `quality_score` (higher is better, max 1.0).

Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

- `routing_accuracy`: fraction of evals.json prompts correctly routed via keyword overlap against SKILL.md frontmatter only
- `heuristic_score`: structural health check (example tags, length)
- KEEP requires: `score >= baseline AND f1 >= baseline_f1` (dual guard prevents keyword-stuffing)

Mutation target: `SKILL.md` — you may ONLY edit this file each iteration.

Locked (never modify):
- `scripts/evaluate.py`
- `scripts/eval_runner.py`
- `evals/evals.json`

How to run one iteration:
1. Edit `SKILL.md` (one focused change per iteration — frontmatter description/triggers only)
2. `python scripts/evaluate.py --skill .agents/skills/eval-autoresearch-fit/SKILL.md --desc "what you changed"`
3. If KEEP (exit 0): `git add SKILL.md && git commit -m "keep: score=X <description>"`
4. If DISCARD (exit 1): evaluate.py already reverted SKILL.md automatically

NEVER STOP. Run until manually interrupted.


## See Also

- [[optimization-program-os-eval-lab-setup]]
- [[optimization-program-os-eval-runner]]
- [[optimization-program-os-eval-lab-setup]]
- [[optimization-program-os-eval-runner]]
- [[karpathy-autoresearch-3-file-eval]]
- [[optimization-program-os-improvement-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/eval-autoresearch-fit/references/program.md`
- **Indexed:** 2026-04-17T06:42:10.074460+00:00
