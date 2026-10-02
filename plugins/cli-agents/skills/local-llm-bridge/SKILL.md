---
name: local-llm-bridge
plugin: cli-agents
description: >
  Local Gemma 4 12B sub-agent. Routes bounded tasks directly to the optimized llama-server
  at localhost:8089 — no routing proxy, no cloud API, 2–5s typical response.
  Use for fast, private, cost-free subtask delegation from any cloud primary agent.
  Part of the run_agent.py multi-LLM task router — cli=llama target.
allowed-tools: Bash, Read, Write
---

# Local LLM Bridge (`local-llm-bridge`)

Dispatches bounded tasks directly to local Gemma 4 12B via llama-server at localhost:8089.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Persona Registry](#-persona-registry-agents)
- [References](#references)

## Constraints

- **Server active**: Requires `llama-server` on port 8089 (`curl -s http://localhost:8089/health`).
- **Prompt budget**: Keep prompts lean (<2,000 tokens) and instructions specific; default `max_tokens=120`.
- **Sub-agent isolation**: Instruct local agent not to use tools or access filesystem. Fast, private delegation (Mode B).

## Quick start

```bash
python3 scripts/run_agent.py agents/refactor-expert.md target.py review.md "List top 3 issues concisely." --cli llama
```

## Workflow

1. **Health Check**: Confirm local llama-server is healthy (`curl -s http://localhost:8089/health`).
2. **Select Persona**: Choose from `agents/security-auditor.md`, `agents/refactor-expert.md`, or `agents/architect-review.md`.
3. **Dispatch**: Run `scripts/run_agent.py` with `--cli llama` and bounded tokens.
4. **Inspect**: Verify the output file contains the completed response.

## Verification

```bash
curl -s http://localhost:8089/health
python3 scripts/run_agent.py /dev/null /dev/null /tmp/test.md "Say hello in one word." --cli llama
cat /tmp/test.md
```

## 🎭 Persona Registry (`agents/`)

These personas are mirrored across CLI agent dispatchers to ensure consistent analytical behavior across the ecosystem.

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

### 🧩 Force Agent Behavior

Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

### 🛠️ Orchestration Pattern: `run_agent.py` (Cross-Platform)

For reusable sub-agent execution, use the provided Python orchestrator which handles temp file assembly and prompt concatenation reliably across Windows, macOS, and Linux:

```bash
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>"
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for local LLM bridge delegation.
- [cheapest_models.md](references/cheapest_models.md) — Local inference latency and token pricing comparison.
