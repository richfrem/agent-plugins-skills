---
concept: github-agentic-workflows-standard
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/reference/github-agentic-workflows.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.049937+00:00
cluster: type
content_hash: b649ad6489871ded
---

# GitHub Agentic Workflows Standard

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# GitHub Agentic Workflows Standard

This document covers the two distinct classes of GitHub AI agents. Both share the `.agent.md` persona format but serve different purposes and require different companion files.

## Quick Comparison

| | Type 1: IDE / UI Agents | Type 2: CI/CD Autonomous Agents |
|---|---|---|
| **Invoked by** | Human in VS Code / GitHub.com Copilot Chat | GitHub Actions event (push, PR, schedule) |
| **Persona file** | `.github/agents/name.agent.md` | `.github/agents/name.agent.md` |
| **Companion file** | `.github/prompts/name.prompt.md` | `.github/workflows/name-agent.yml` |
| **Human loop** | Yes — human reviews, chains onwards | No — fully autonomous gate |
| **Key frontmatter** | `handoffs:`, `tools:`, `model:` | Kill Switch phrase in body |
| **Trigger** | Slash command or agent dropdown | `on: push`, `pull_request`, `schedule` |

---

## Type 1: IDE / UI Agents (Interactive Copilot Agents)

Invoked by a developer directly within **GitHub Copilot Chat** in VS Code or GitHub.com. These are **human-in-the-loop** agents that perform workflows on demand and can chain to other agents via `handoffs`.

### `.agent.md` Frontmatter (2025 Standard)

```yaml
---
description: What this agent does (shown in agent picker UI)
handoffs:
  - label: Friendly button label for next step
    agent: target-agent-name        # references another .agent.md by name
    prompt: Pre-filled handoff message for the user
    send: true                      # auto-send (true) or let user edit first (false)
tools:                              # Optional: restrict to specific tools
  - github
  - terminal
model: claude-3.5-sonnet           # Optional: override model
mcp-servers:                       # Optional: MCP server integrations
  my-server:
    command: node
    args: ["./mcp-server.js"]
---
```

> **Note:** The `name:` frontmatter key is legacy. The filename (`name.agent.md`) serves as the agent's identifier. `description:` is shown in the agent picker. As of November 2025, `.chatmode.md` files are officially renamed to `.agent.md`.

### `.prompt.md` Companion File

Every IDE agent needs a thin companion pointer in `.github/prompts/`. This file registers the slash command:

```yaml
---
agent: agent-name-without-extension
---
```

That's it. The file is intentionally minimal — the instructions live entirely in the `.agent.md`.

### IDE Agent Use Cases
- Spec-driven workflows (specify → plan → tasks → implement)
- On-demand code reviews with chained handoffs
- Interactive analysis agents (triggered manually on specific files/branches)
- Documentation generators invoked from within the editor

---

## Type 2: CI/CD Autonomous Agents (Smart Failure / Agentic DevOps)

Triggered autonomously by GitHub Actions. These agents fire on repository events (PR opened, push to main, daily schedule) and can **fail the build** if they detect issues — no human required.

Use cases:
- **Continuous triage**: Auto-label and route new issues
- **Continuous documentation**: Keep READMEs aligned with code changes
- **Quality gates**: Verify PRs meet acceptance criteria or spec alignment
- **Security scanning**: Detect CVEs, unsafe patterns, or compliance violations

### Safety Architecture
By default the agent is **read-only**. Write operations (creating PRs with fixes) require separate jobs after the analysis job completes. A `SafeOutputs` subsystem can filter outputs before committing changes.

### The Smart Failure Architecture
A closed-loop system requiring two files:

1. **The Persona** (`.github/agents/name.agent.md`): Same format as Type 1. Must define a specific **Kill Switch phrase** the agent outputs on failure.
2. **The Runner** (`.github/workflows/name-agent.yml`): Installs Copilot CLI, runs the persona headlessly, greps output for the Kill Switch phrase, exits non-zero to block the PR.

#### Component 1: The Persona (System Prompt) Example
The most critical part of this workflow is Prompt Engineering. The agent must act as an auditor.


*(content truncated)*

## See Also

- [[github-models-prompts-standard]]
- [[github-models-prompts-standard]]
- [[github-models-prompts-standard]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agentic-os-setup-orchestrator]]
- [[agentic-os-architecture]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/reference/github-agentic-workflows.md`
- **Indexed:** 2026-04-17T06:42:10.049937+00:00
