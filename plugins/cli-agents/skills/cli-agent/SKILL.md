---
name: cli-agent
plugin: cli-agents
description: Dispatches bounded tasks, reviews, and audits through external CLI coding agents (Claude, Codex, Copilot, Agy, and local llama-server), with server lifecycle and model catalog maintenance.
allowed-tools: Bash, Read, Write
---

# CLI Agent (`cli-agent`)

Unified multi-LLM task router and execution engine for external CLI agents and local models.

## Contents

- [Constraints](#constraints) • [Quick Start](#quick-start) • [Backends](#supported-backends--dispatch) • [Workflow](#workflow) • [Verification](#verification) • [Setup & Maintenance](#setup--maintenance) • [Personas](#personas) • [References](#references)

## Constraints

- **Authorization & Isolation**: Analysis uses `--isolated` to suppress hazardous flags; non-isolated execution requires explicit user authorization. With `--isolated`, `run_agent.py` wraps input in `---SOURCE---` … `---END SOURCE---` and appends the isolation instruction. Without `--isolated` (including `--cli llama`), add that instruction to the prompt yourself:
  > "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."
- **Fail-Closed & Single Backend**: Use one backend per task; halt immediately on failure without silent fallback. See [fallback-tree.md](references/fallback-tree.md) and [execution-contract.md](references/execution-contract.md).
- **Reproducibility & Scope**: Reuse the caller's runtime/model/effort choice; do not start an unrequested review. Record executable versions, tokens, and outputs.

## Quick Start

```bash
python3 scripts/run_agent.py <personas>/security-auditor.md <input> <output> "Review supplied source." --cli claude --isolated --require-input
```

## Supported Backends & Dispatch

| Backend | CLI Flag | Target Runtime / Engine | Dispatch Reference |
| :--- | :--- | :--- | :--- |
| **Claude** | `--cli claude` | Claude Code CLI (Sonnet / Opus) | [claude-cli-dispatch.md](references/claude-cli-dispatch.md) |
| **Codex** | `--cli codex` | OpenAI Codex CLI (GPT-5 / o-series) | [codex-cli-dispatch.md](references/codex-cli-dispatch.md) |
| **Copilot** | `--cli copilot` | GitHub Copilot CLI | [copilot-cli-dispatch.md](references/copilot-cli-dispatch.md) |
| **Antigravity** | `--cli agy` | Google Antigravity / Gemini CLI | [agy-cli-dispatch.md](references/agy-cli-dispatch.md) |
| **Local LLM** | `--cli llama` | Local Gemma 4 12B at localhost:8089 | [local-llm-dispatch.md](references/local-llm-dispatch.md) |

## Workflow

1. **Select Backend & Persona**: Check [backend capabilities](references/backend-capabilities.md) and [cheapest models](references/cheapest_models.md). Choose a persona from `<personas>/` (see [Personas](#personas)).
2. **Dispatch & Verify**: Execute `scripts/run_agent.py` with `--cli <backend>`. Verify exit 0 and non-empty output. Empty or failed output is not a completed review.

## Verification

For gated reviews, record the result through control-plane `record-critic-review PASS|REVISE|REJECT`; only PASS approves. Verify compliance against [acceptance-criteria.md](references/acceptance-criteria.md).

## Setup & Maintenance

- **Project Setup & Catalogs**: Follow [project setup](references/project-setup.md), [capability baseline](references/project-capability-baseline.md), [workflow](references/project-configuration-workflow.md), [profile contract](references/capability-profile-contract.md), and [catalog maintenance](references/model-catalog-maintenance.md). Update catalog: `python3 scripts/sync_cheapest_models.py --repository . --dry-run` (refresh neither authorizes model calls nor starts reviews).
- **Local LLM & Specs**: Start llama-server: `python3 scripts/run_server.py` (see [deep reference](references/local-llm-setup-deep-reference.md), [latency findings](references/routing_latency_findings.md), [proxy diagram](references/routing-proxy.mmd), and [debrief](references/local_llm_debrief.md)). Inspect [Claude spec](references/claude-directory-spec.md), [Claude settings](references/claude-settings-schema.md), [Antigravity spec](references/antigravity-directory-spec.md), [Gemini commands](references/gemini-cli-commands.md), [Codex fixture](references/p0-codex-observation-fixture.json), and [map debt](references/map-debt.md).

## Personas

`<personas>` is the cli-agents host sub-agent directory, not part of this skill: the cli-agents plugin's top-level `agents/` folder in a source checkout, or the harness's installed agents (e.g. `.claude/agents/`). Any prompt file or `/dev/null` also works. Common: `security-auditor.md`, `refactor-expert.md`, `architect-review.md`, `red-team-reviewer.md`.

Without `--isolated`, add to the prompt: "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

## References

- [Project Setup](references/project-setup.md) • [Capability Baseline](references/project-capability-baseline.md) • [Workflow](references/project-configuration-workflow.md) • [Profile Contract](references/capability-profile-contract.md) • [Acceptance Criteria](references/acceptance-criteria.md)
- [Backend Capabilities](references/backend-capabilities.md) • [Execution Contract](references/execution-contract.md) • [Fallback Tree](references/fallback-tree.md) • [Cheapest Models Reference](references/cheapest_models.md) • [Model Catalog Maintenance](references/model-catalog-maintenance.md)
- [Local LLM Setup Reference](references/local-llm-setup-deep-reference.md) • [Local LLM Debrief](references/local_llm_debrief.md) • [Routing Latency Findings](references/routing_latency_findings.md) • [Routing Proxy Diagram](references/routing-proxy.mmd) • [Map Debt](references/map-debt.md)
- [Claude Directory Spec](references/claude-directory-spec.md) • [Claude Settings Schema](references/claude-settings-schema.md) • [Antigravity Directory Spec](references/antigravity-directory-spec.md) • [Gemini CLI Commands](references/gemini-cli-commands.md) • [Codex Fixture](references/p0-codex-observation-fixture.json)
