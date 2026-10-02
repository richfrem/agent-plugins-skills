---
name: agy-cli-agent
plugin: cli-agents
description: Dispatches authorized tasks through Antigravity (agy) to Gemini and other agy-hosted models. Use for agy execution, Gemini tasks, or an agy sub-agent.
allowed-tools: Bash, Read, Write
---

# Agy CLI Agent

Dispatch the authorized task using the bundled router.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Persona Registry](#-persona-registry-agents)
- [Dispatch details](references/agy-cli-dispatch.md)

## Constraints

Reuse the user's runtime/model/effort choice; do not start an unrequested review.
Use one backend; halt on failure without silent fallback. Analysis uses `--isolated`;
it suppresses dangerous flags and adds instructions, but is not an OS sandbox.
Non-isolated dispatch requires authorization and external containment where needed.

## Quick start

Run from this skill root; input and output paths are supplied by the caller:

```bash
python3 scripts/run_agent.py agents/security-auditor.md <input> <output> "Review supplied source." --cli agy --isolated --require-input
```

## Workflow

1. Read [dispatch details](references/agy-cli-dispatch.md) before selecting flags or models.
2. Read [execution rules](references/execution-contract.md) and [backend capabilities](references/backend-capabilities.md); user instructions govern authorization.
3. Use the selected model and optional effort; inspect the resolved executable/version.
4. Dispatch once, then check exit status, nonempty output and requested acceptance criteria.

[Profile contract](references/capability-profile-contract.md) applies when a caller supplies a profile.

## Verification

Record backend, executable/version, model, effort, scope and result. Empty or failed
output is not a completed review. Log failures in [Map Debt](references/map-debt.md).
For gated reviews, record PASS/REVISE/REJECT through the control plane; only PASS approves.

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
