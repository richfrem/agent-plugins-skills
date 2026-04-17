---
concept: optimization-program-os-eval-lab-setup
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-lab-setup/references/program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.144046+00:00
cluster: plugin-code
content_hash: 8531144e88084aea
---

# Optimization Program: os-eval-lab-setup

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Optimization Program: os-eval-lab-setup

Goal: maximize `quality_score` (higher is better, max 1.0).
Formula: `quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)`

Mutation target: `SKILL.md` — only this file changes each iteration.
Locked: `evals/evals.json`, `evaluate.py`, `eval_runner.py`

How to run one iteration (from within this skill's directory):
```bash
python3 ../os-eval-runner/scripts/evaluate.py \
  --skill . \
  --desc "what changed"
```

NEVER STOP. Run until target score or human interruption.

## Notes
- **Optimizing**: Routing accuracy for os-eval-lab-setup — triggers on SETUP/BOOTSTRAP requests for isolated eval lab repos, NOT on running the actual eval loop or backporting results
- **Target score**: 0.95
- **Baseline**: starting fresh with formal tracking
- **Key failure modes**: Confusion with os-eval-runner (run loop) vs os-eval-backport (review results) — this skill is only for SETUP
- **Meta-circular note**: This skill sets up the very infrastructure that evaluates it. The lock on evals.json prevents the agent from gaming the metric by changing what "set up eval lab" means.


## See Also

- [[optimization-program-os-eval-runner]]
- [[optimization-program-os-eval-runner]]
- [[identity-the-eval-lab-setup-agent]]
- [[optimization-program-os-improvement-loop]]
- [[optimization-program-eval-autoresearch-fit]]
- [[optimization-program-eval-autoresearch-fit]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-lab-setup/references/program.md`
- **Indexed:** 2026-04-17T06:42:10.144046+00:00
