---
name: claude-cli-agent
plugin: cli-agents
description: >
  Claude CLI sub-agent system for dispatching tasks and persona-based analysis to
  Anthropic Claude models. Use for task delegation, security audits, architecture reviews, 
  or any work requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

# Claude CLI Sub-Agent Conductor

Delegates tasks to Anthropic model backends via the central Conductor script.

## Core Dispatch Pattern

To invoke a Claude sub-agent, call the central Conductor with the `--backend claude` parameter.

### Task Dispatch:
```bash
python3 plugins/cli-agents/scripts/conductor.py \
  --backend claude \
  --persona /dev/null \
  --input tasks/todo/prompt.md \
  --output temp/output.md \
  --instruction "Generate the files requested." \
  --model haiku-4.5 \
  --allow-tools
```

### Isolated Analysis (No tools, read-only):
```bash
python3 plugins/cli-agents/scripts/conductor.py \
  --backend claude \
  --persona plugins/cli-agents/agents/security-auditor.md \
  --input target.py \
  --output temp/review.md \
  --instruction "Find security flaws." \
  --model haiku-4.5
```
