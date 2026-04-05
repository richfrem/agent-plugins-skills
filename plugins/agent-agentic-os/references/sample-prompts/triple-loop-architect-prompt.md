# Triple-Loop Architect — Sample Test Prompt

Use this prompt to trigger the `triple-loop-architect` agent for an end-to-end autonomous eval run.
Adjust `<skill-name>` and `<plugin-folder>` to target a different skill.

---

## 🧪 Prompt (copy/paste to use)

```
@triple-loop-architect

Kick off a 10-iteration Triple-Loop optimization run targeting the `convert-mermaid` skill
inside the `mermaid-to-png` plugin.

## Setup
- Bootstrap a clean sibling lab at `~/Projects/test-convert-mermaid-eval`
- Hard-copy plugin files with `cp -RL` (not rsync)
- Install `os-eval-runner` and `copilot-cli-agent` into the lab via `plugin_add.py --all -y`
- Verify `evaluate.py` and `plot_eval_progress.py` are present before proceeding
- Fill ALL placeholders in `eval-instructions.md` — do not leave any `{{...}}` unreplaced
- Confirm the evals.json has `should_trigger` boolean schema
- Run the readiness checklist before handing off to L1

## Orchestration
- L1 orchestrator: `gemini --yolo --model gemini-3-flash-preview`
- L2 mutation proposer: `copilot` with `gpt-mini` and `--allow-all-paths --allow-all-urls -y`
- Log output to: `temp/gemini_orchestrator_convert-mermaid.log`
- Generate `eval_progress.png` at the end of the run using `plot_eval_progress.py`

## Goal
Improve the routing precision and trigger descriptions of the `convert-mermaid` SKILL.md
across 10 autonomous KEEP/DISCARD hypothesis iterations. Do not pause or ask for confirmation
at any point during the loop. When the run is complete, tell me so I can run the backport.
```

---

## 🔄 Alternate: Different Skill

To target a different skill, change the skill/plugin names:

```
@triple-loop-architect

Kick off a 10-iteration Triple-Loop optimization run targeting the `<skill-name>` skill
inside the `<plugin-folder>` plugin.

Bootstrap a clean sibling lab at `~/Projects/test-<skill-name>-eval`.
Use gemini-3-flash-preview as the L1 orchestrator and gpt-mini as the L2 proposer.
Run the full readiness checklist before dispatching. Log to temp/gemini_orchestrator_<skill-name>.log.
```

---

## 📊 Monitoring Commands (run from `agent-plugins-skills` root)

```bash
# Watch live log
tail -f temp/gemini_orchestrator_convert-mermaid.log

# Check iteration scores
cat ~/Projects/test-convert-mermaid-eval/mermaid-to-png/skills/convert-mermaid/evals/results.tsv

# Regenerate chart manually at any point
python3 plugins/agent-agentic-os/scripts/plot_eval_progress.py \
  --tsv ~/Projects/test-convert-mermaid-eval/mermaid-to-png/skills/convert-mermaid/evals/results.tsv \
  --out ~/Projects/test-convert-mermaid-eval/mermaid-to-png/skills/convert-mermaid/evals/eval_progress.png
```

---

## ✅ When Complete

Say: `backport convert-mermaid` to trigger the `os-eval-backport` skill and review improvements.
