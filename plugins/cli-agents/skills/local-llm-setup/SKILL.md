---
name: local-llm-setup
plugin: cli-agents
description: >
  Cross-platform setup wizard for the local Gemma 4 12B inference stack. Automates
  llama-server installation (binary download or Metal/CUDA/Vulkan/ROCm compile),
  model download, routing proxy daemon install (launchd/systemd/NSSM), and
  Mode A/B validation. Covers Day 1 bootstrap and Day 2+ reconfiguration.
allowed-tools: Bash, Read, Write
---

# Local LLM Setup (`local-llm-setup`)

Setup wizard and configuration guide for local Gemma 4 12B inference and task delegation.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Persona Registry](#-persona-registry-agents)
- [References](#references)

## Constraints

- **Hardware acceleration**: Auto-detects and compiles for Metal (macOS), CUDA, Vulkan, or ROCm.
- **Modes**: Mode B (`run_agent.py --cli llama`) for delegation; Mode A (`scripts/enable_global_routing.py`) for proxy.
- **Paths**: All scripts resolve from `scripts/` relative to skill root.

## Quick start

```bash
python3 scripts/run_server.py
curl -s http://localhost:8089/health
```

## Workflow

1. **Bootstrap**: Review prerequisites in `references/local-llm-setup-deep-reference.md`.
2. **Launch Server**: Start `llama-server` on port 8089 (`python3 scripts/run_server.py`).
3. **Validate**: Run Mode B test command and confirm sub-5s response latency.

## Verification

```bash
python3 scripts/run_agent.py agents/refactor-expert.md target.py output.md "List top 3 issues." --cli llama
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

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for local LLM setup.
- [local-llm-setup-deep-reference.md](references/local-llm-setup-deep-reference.md) — Platform-specific compilation, model download, and service guides.
