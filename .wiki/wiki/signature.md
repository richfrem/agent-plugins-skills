---
concept: signature
source: plugin-code
source_file: copilot-cli/skills/copilot-cli-agent/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.550765+00:00
cluster: model
content_hash: 96ecd608eda1d5f2
---

# Signature:

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: copilot-cli-agent
description: >
  Copilot CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to GitHub Copilot models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## 🎭 Identity: The Sub-Agent Dispatcher (Standard: gpt-5-mini)

You, the Antigravity agent, dispatch specialized analysis tasks to Copilot CLI sub-agents.

> [!IMPORTANT]
> **Default model: `gpt-5-mini` (free tier — no per-request cost).** Use this unless the user explicitly requests a premium model. Premium models (e.g., `claude-sonnet-4-6`) are **charged per request**, not per token — see the [💰 Premium Model Cost Discipline](#-premium-model-cost-discipline) section before using them.

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
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" [MODEL]
#                                                                                           ^ optional 5th arg
```

---

## 🔀 Model Selection Guide

### Default: `gpt-5-mini` (Free — use for most tasks)

```bash
# No model arg = gpt-5-mini (free tier, no per-request cost)
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Find vulnerabilities."
```

### Premium: `claude-sonnet-4-6` (Charged per request — batch everything)

```bash
# Pass model name as the 5th argument to override the default
python ./scripts/run_agent.py /dev/null /tmp/copilot_prompt.md /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4-6
```

> [!NOTE]
> **When to use `claude-sonnet-4-6`:** Complex multi-file generation, nuanced content requiring reasoning, tasks where output quality matters more than cost. See [💰 Premium Model Cost Discipline](#-premium-model-cost-discipline) for request-batching rules before calling.

### Known Model Identifiers

| Model | Identifier | Cost |
|:---|:---|:---|
| GitHub Copilot default | `gpt-5-mini` | Free / flat rate |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Per request (premium) |
| Claude Opus | `claude-opus-4-5` | Per request (premium, highest quality) |

> [!WARNING]
> Model identifiers can change with Copilot CLI updates. If a premium model call fails with a model-not-found error, check `copilot --help` or the [GitHub Copilot model docs](https://docs.github.com/en/copilot/using-github-copilot/ai-models) for the current identifier.

---

## 🎭 Persona Registry (`agents/`)

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

---

## ⚠️ CLI Best Practices & Failure Modes

### 1. ❌ Why Stdin Piping Fails
Using `cat code.py | copilot -p "review this"` is unreliable. The CLI often prioritizes the prompt flag and ignores the piped input. **Always embed the code** inside the command string as shown in the Core Pattern.

### 2. ❌ Empty Output (Background Runs)
Large prompt expansions (e.g., `$(cat ...)` > 10KB) can silently fail when run in the background (`

*(content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `copilot-cli/skills/copilot-cli-agent/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.550765+00:00
