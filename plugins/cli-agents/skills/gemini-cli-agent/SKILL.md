---
name: gemini-cli-agent
plugin: cli-agents
description: >
  Gemini CLI sub-agent system for dispatching tasks and persona-based analysis to
  Google Gemini models. Use for task delegation, security audits, architecture reviews, 
  or any work requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

# Gemini CLI Sub-Agent Conductor

Delegates tasks to Google Gemini model backends via the central Conductor script.

## Core Dispatch Pattern

To invoke a Gemini sub-agent, call the central Conductor with the `--backend gemini` parameter.

### Task Dispatch:
```bash
python3 plugins/cli-agents/scripts/conductor.py \
  --backend gemini \
  --persona /dev/null \
  --input tasks/todo/prompt.md \
  --output temp/output.md \
  --instruction "Generate the files requested." \
  --model gemini-3-flash-preview \
  --allow-tools
```

### Isolated Analysis (No tools, read-only):
```bash
python3 plugins/cli-agents/scripts/conductor.py \
  --backend gemini \
  --persona plugins/cli-agents/agents/security-auditor.md \
  --input target.py \
  --output temp/review.md \
  --instruction "Find security flaws." \
  --model gemini-3-flash-preview
```
