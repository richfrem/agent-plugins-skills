---
name: copilot-cli-agent
plugin: cli-agents
description: >
  Copilot CLI sub-agent system for dispatching tasks and persona-based analysis to
  GitHub Copilot models. Use for task delegation, security audits, architecture reviews, 
  or any work requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

# Copilot CLI Sub-Agent Conductor

Delegates tasks to GitHub Copilot model backends via the central Conductor script.

## Core Dispatch Pattern

To invoke a Copilot sub-agent, call the central Conductor with the `--backend copilot` parameter.

### Task Dispatch (Allowing tools/writes - Non-isolated):
```bash
python3 plugins/cli-agents/scripts/conductor.py \
  --backend copilot \
  --persona /dev/null \
  --input tasks/todo/prompt.md \
  --output temp/output.md \
  --instruction "Generate the files requested." \
  --model claude-sonnet-4.6 \
  --allow-tools
```

### Isolated Analysis (No tools, read-only):
```bash
python3 plugins/cli-agents/scripts/conductor.py \
  --backend copilot \
  --persona plugins/cli-agents/agents/security-auditor.md \
  --input target.py \
  --output temp/review.md \
  --instruction "Find security flaws." \
  --model gpt-5-mini
```
*(Default execution is isolated; omit `--allow-tools` for sandboxed read-only runs).*
