---
concept: optimization-program-copilot-cli-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/copilot-cli-agent/references/program.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.754552+00:00
cluster: target
content_hash: 87e7adf7ab6fc5f2
---

# Optimization Program: copilot-cli-agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[optimization-program-gemini-cli-agent]]
- [[optimization-program-gemini-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/copilot-cli-agent/references/program.md`
- **Indexed:** 2026-04-17T06:42:09.754552+00:00
