---
concept: signature
source: plugin-code
source_file: copilot-cli/skills/copilot-cli-agent/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.964075+00:00
cluster: agent
content_hash: 97c7f518fb2a041f
---

# Signature:

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: copilot-cli-agent
description: >
  Copilot CLI sub-agent system for dispatching tasks and persona-based analysis to
  GitHub Copilot models. Use for task delegation (agent reads/writes files directly),
  security audits, architecture reviews, or any work requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## 🎭 Identity: The Sub-Agent Dispatcher (Standard: gpt-5-mini)

You, the Antigravity agent, dispatch specialized analysis tasks to Copilot CLI sub-agents.

> [!IMPORTANT]
> **Default model: `gpt-5-mini` (free tier — no per-request cost).** Use this unless the user explicitly requests a premium model. Premium models (e.g., `claude-sonnet-4.6`) are **charged per request**, not per token — see the [💰 Premium Model Cost Discipline](#-premium-model-cost-discipline) section before using them.

### ✅ Minimal Working Code Review Agent Pattern

To ensure Copilot CLI behaves as a specialized persona rather than a generic responder, **always** embed the persona and source material directly into the prompt flag (`-p`).

```bash
copilot -p "$(cat agents/persona.md)

---SOURCE CODE---
$(cat target.py)

---INSTRUCTION---
Perform a full code review. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR.
You are operating as an isolated sub-agent.
Do NOT use tools. Do NOT access filesystem." > review.md
```

---

## 🛠️ Orchestration Pattern: `run_agent.py` (Cross-Platform)

For reusable sub-agent execution, use the provided Python orchestrator which handles temp file assembly and prompt concatenation reliably across Windows, macOS, and Linux.

```bash
# Signature:
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" [MODEL] [isolated]
#                                                                                           ^        ^
#                                                                                           optional optional (default: false)
```

### Two dispatch modes

**Task dispatch** (default — agent has full filesystem access via `--yolo`):
```bash
# Agent reads/writes files directly. Pass the task prompt as INPUT_FILE.
python plugins/copilot-cli/scripts/run_agent.py \
  /dev/null \
  tasks/todo/copilot_prompt_0025.md \
  temp/copilot_output_0025.md \
  "Implement all changes specified in the prompt." \
  claude-sonnet-4.6
```

**Isolated analysis** (no filesystem tools — text output only):
```bash
# Pass isolated=true as 6th arg. Agent generates text output only.
python plugins/copilot-cli/scripts/run_agent.py \
  agents/security-auditor.md target.py security.md \
  "Find vulnerabilities." gpt-5-mini true
```

### Prompt assembly (handled automatically by `run_agent.py`)

| Inputs present | Assembled prompt |
|:---|:---|
| persona + input | `persona / ---SOURCE--- input / ---INSTRUCTION--- instruction` |
| input only (task dispatch) | `input / ---INSTRUCTION--- instruction` |
| instruction only (heartbeat) | `instruction` |

Passing `/dev/null` for persona or input skips that block cleanly.

---

## 🔀 Model Selection Guide

### Default: `gpt-5-mini` (Free — use for most tasks)

```bash
# No model arg = gpt-5-mini (free tier, no per-request cost)
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Find vulnerabilities."
```

### Premium: `claude-sonnet-4.6` (Charged per request — batch everything)

```bash
# Pass model name as the 5th argument to override the default
python ./scripts/run_agent.py /dev/null /tmp/copilot_prompt.md /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4.6
```

> [!NOTE]
> **When to use `claude-sonnet-4.6`:** Complex multi-file generation, nuanced content requiring reasoning, tasks where output quality matters more than cost. See [💰 Premium Model Cost Discipline](#-premium-model-cost-discipline) for request-batching rules before calling.

### Known Model Identifiers

| Model | Identifier | Cost |
|:---|:---|:---|
| GitHub Copilot defa

*(content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `copilot-cli/skills/copilot-cli-agent/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.964075+00:00
