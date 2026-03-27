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

*Example: `.github/agents/dependency-updater.agent.md`*
```markdown
---
name: dependency-updater-agent
description: Keep dependencies current across the MCP servers monorepo by auditing packages, proposing safe upgrades, and coordinating updates contextually.
---

# 📦 Dependency Updater Agent Instructions

**Purpose:** Identify, evaluate, and implement dependency updates while preserving stability.

## 🎯 Core Workflow
### 1. Scope the Update
- Collect current dependency manifests (`package.json`, `pnpm-lock.yaml`, `pyproject.toml`, `go.mod`).
- Identify direct vs. transitive dependencies.

### 2. Assess Upgrade Impact
- Use tooling: `pnpm outdated`, `uv pip list --outdated`, `go list -u -m all`.
- Review changelogs/semver impacts for breaking changes.

... [Additional workflow instructions specific to the agent's task] ...

### Kill Switch / Quality Gate
- If a proposed dependency introduces a known CVE, outputs exactly: `CRITICAL DEPENDENCY VULNERABILITY DETECTED`
```
*(Source: [VeVarunSharma/contoso-vibe-engineering](https://github.com/VeVarunSharma/contoso-vibe-engineering/blob/main/.github/agents/dependency-updater.agent.md))*

### Component 2: Example Security Agent Action
Here is the structural implementation of an Agentic DevOps action that fails the build if critical vulnerabilities are found using the persona above:

```yaml
jobs:
  security-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Install Intelligence
        run: npm i -g @github/copilot

      - name: Run Agent via Copilot CLI
        env:
          COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          
          # 1. Load the Persona / System Prompt
          AGENT_PROMPT=$(cat .github/agents/security-reporter.agent.md)
          
          # 2. Add Dynamic Context
          PROMPT="$AGENT_PROMPT"
          PROMPT+=$'\n\nTask: Execute instructions and generate report at /report.md'
          
          # 3. Execute Headless (prevent interactive wait)
          copilot --prompt "$PROMPT" --allow-all-tools --allow-all-paths < /dev/null

      - name: The Logic Check (Smart Fail)
        if: always()
        run: |
          # 4. Grep for the exact Kill Switch phrase defined in the prompt
          if grep -q "THIS ASSESSMENT CONTAINS A CRITICAL VULNERABILITY" report.md; then
            echo "❌ CRITICAL VULNERABILITY DETECTED - Workflow failed"
            exit 1 # Breaks the build
          else
            echo "✅ No critical vulnerabilities detected"
          fi
```

### Advantages & Drawbacks
- **Pros:** Contextual understanding of code intent, reduces code review fatigue, easily enforces product acceptance criteria or documentation rules.
- **Cons:** LLMs are non-deterministic (prone to false positives/negatives), slower than traditional linters, and prone to hallucinations. **Mitigation:** Use strict "Intentional Vulnerability" filters in your System Prompt so the AI knows what to ignore.

---

## Type 3: Official GitHub Agentic Workflows (Technical Preview — Feb 2026)

> **Source:** [github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)

This is the **official GitHub platform feature** from GitHub Next, now in technical preview. It is meaningfully different from the Smart Failure pattern above — it uses a dedicated Markdown format with native `safe-outputs` and a compiled lock file. **Prefer this format for new agentic workflows when the preview is available.**

### Key Differences from Smart Failure

| | Smart Failure (Type 2) | Official Agentic Workflows (Type 3) |
|---|---|---|
| **Persona file** | `.github/agents/*.agent.md` | `.github/workflows/name.md` |
| **Runner file** | `.github/workflows/name.yml` (hand-crafted) | `.github/workflows/name.lock.yml` (compiled) |
| **Failure signaling** | Kill Switch phrase + grep | Native `safe-outputs` guardrails |
| **Permissions** | Declared in YAML runner | Declared in Markdown frontmatter |
| **Safety model** | Read-only by convention | Read-only by default, enforced by platform |
| **Coding engines** | Copilot CLI (only) | Copilot CLI, Claude Code, OpenAI Codex |
| **Compilation step** | None | `gh aw compile` (requires `gh-aw` extension) |
| **Status** | Works today (any repo) | Technical preview (Feb 2026) |

### Official Agentic Workflow File Format

Two files are generated — one Markdown (your intent) and one lock file (compiled, committed).

**`.github/workflows/daily-repo-status.md`**
```markdown
---
on:
  schedule: daily

permissions:
  contents: read
  issues: read
  pull-requests: read

safe-outputs:
  create-issue:
    title-prefix: "[repo status] "
    labels: [report]
  create-pull-request: {}   # Allow PR creation (write op, requires opt-in)
  add-comment: {}           # Allow issue/PR comments

tools:
  github:                   # GitHub context tools
---

# Daily Repo Status Report

Create a daily status report for maintainers.

Include:
- Recent repository activity (issues, PRs, discussions, releases, code changes)
- Progress tracking, goal reminders and highlights
- Project status and recommendations
- Actionable next steps for maintainers

Keep it concise and link to the relevant issues/PRs.
```

#### Frontmatter Fields

| Field | Purpose | Example |
|---|---|---|
| `on.schedule` | Cron or natural language schedule | `daily`, `weekly`, `0 9 * * 1` |
| `on.push` / `on.pull_request` | Event-based triggers | Standard GitHub Actions syntax |
| `permissions` | Explicit read/write grants | `contents: read`, `issues: write` |
| `safe-outputs` | Allowlisted write operations | `create-issue`, `create-pull-request`, `add-comment` |
| `tools` | Tool namespaces available to agent | `github:`, `terminal:` |

#### Compile Step

```bash
# Install the gh-aw extension
gh extension install github/gh-aw

# Compile the .md into a .lock.yml
gh aw compile

# Commit both files
git add .github/workflows/daily-repo-status.md .github/workflows/daily-repo-status.lock.yml
git commit -m "feat: add daily repo status agentic workflow"
```

### Official Use Cases (from GitHub Next)
- **Continuous triage**: Automatically summarize, label, and route new issues
- **Continuous documentation**: Keep READMEs aligned with code changes
- **Continuous code simplification**: Repeatedly identify code improvements, open PRs
- **Continuous test improvement**: Assess coverage, add high-value tests
- **Continuous quality hygiene**: Investigate CI failures, propose fixes
- **Continuous reporting**: Daily/weekly repository health reports

### Safety Architecture
Workflows run with **read-only permissions by default**. Write operations (creating PRs, adding comments) require explicit declaration in `safe-outputs` — they're sandboxed, reviewed, and never merged automatically. Designed with defense-in-depth against prompt injection.

> **Billing:** Each workflow run typically incurs ~2 Copilot premium requests (one for agentic work, one for guardrail check). Configure the model to manage costs.

---

## Quick Reference: Which Format Do I Use?

| Goal | Use |
|---|---|
| Run tests, build, deploy (deterministic) | Traditional GitHub Actions (`.yml` only) |
| AI review gate that fails a PR | Smart Failure (Type 2) — works today |
| Daily AI-powered repo automation | Official Agentic Workflow (Type 3) — technical preview |
| Invokable from Copilot Chat in VS Code | IDE Agent (Type 1) — `.agent.md` + `.prompt.md` |

Use the `create-agentic-workflow` skill to scaffold Type 2 (`--format smart-failure`) or Type 3 (`--format official`).
Use the `create-github-action` skill to scaffold traditional CI/CD pipelines.

