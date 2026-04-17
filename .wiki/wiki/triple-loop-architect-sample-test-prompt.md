---
concept: triple-loop-architect-sample-test-prompt
source: plugin-code
source_file: agent-agentic-os/references/sample-prompts/triple-loop-architect-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.147377+00:00
cluster: skill
content_hash: b342ecb4af935a88
---

# Triple-Loop Architect — Sample Test Prompt

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Triple-Loop Architect — Sample Test Prompt

Use this prompt to trigger the `triple-loop-architect` agent for an end-to-end autonomous eval run.
Adjust `<skill-name>` and `<plugin-folder>` to target a different skill.

## What This Does

The Triple-Loop runs three tiers of agents autonomously:
- **L0 (you + Claude)** — scaffolds an isolated sibling lab repo, seeds all required files, launches L1
- **L1 (Gemini Flash, `--yolo`)** — headless overnight orchestrator, reads `eval-instructions.md`, loops
- **L2 (Copilot `gpt-5-mini`)** — cheap mutation proposer using free Copilot quota

`evaluate.py` gates every iteration: exit 0 = KEEP, exit 1 = DISCARD + auto-revert. The loop runs unattended.

**Real result — `convert-mermaid`, 26 iterations across 2 rounds:**

![convert-mermaid eval progress](../../../../mermaid-to-png/skills/convert-mermaid/evals/eval_progress.png)

Score went from **0.61 → 1.00**. The two-segment shape shows a fresh baseline for round 2 — the plotter handles this automatically. Each green dot is a new record. Each blue diamond is a session baseline.

> **Not every skill is a good candidate.** The best targets have clear routing criteria and good adversarial eval cases. Run [`eval-autoresearch-fit`](../../../agent-plugin-analyzer/skills/eval-autoresearch-fit/SKILL.md) first if unsure.

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


## See Also

- [[triple-loop-architect-sibling-lab-setup]]
- [[triple-loop-architect-sibling-lab-setup]]
- [[triple-loop-architect-sibling-lab-setup]]
- [[triple-loop-orchestrator-unattended-supervisor]]
- [[triple-loop-learning-system---architecture-overview]]
- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/references/sample-prompts/triple-loop-architect-prompt.md`
- **Indexed:** 2026-04-17T06:42:09.147377+00:00
