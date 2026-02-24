# GitHub Agentic Workflows Standard

This document outlines the standard for integrating with **GitHub Agentic Workflows**, a system designed by GitHub Next to bring "Continuous AI" into the CI/CD loop. 

## Background Research
While GitHub Models (`.prompt.yml`) are used for static, user-invoked prompt templates, **GitHub Agentic Workflows** are designed to run autonomously in the background via GitHub Actions responding to repository events (like an issue creation, a PR open, or on a daily schedule).

GitHub Agentic Workflows leverage the power of LLMs (Claude Code, OpenAI Codex, or Copilot) to execute subjective, repetitive toil that traditional deterministic CI/CD pipelines struggle with. Examples include:
- **Continuous triage**: Automatically summarizing, labeling, and routing new issues.
- **Continuous documentation**: Keeping READMEs aligned with code changes.
- **Continuous quality hygiene**: Proactively investigating CI failures.

### Safety Architecture
The system employs a strict safety model. The agent is fundamentally **read-only** by default. Write operations (such as making pull requests) are deferred and must pass through validation phases or be executed as separate jobs after the agent finishes its logic. A `SafeOutputs` subsystem filters outputs to enforce project policies before changes are committed.

## The Output Format
When authoring these, the architecture requires two files:
1. A standard GitHub Action YAML file to handle the infrastructural trigger and runner.
2. A **Markdown file** that serves as the "agentic authoring" payload.

This Markdown file consists of a YAML frontmatter block to declare permissions, schedules, and tools, followed by natural English instructions.

### Example Agentic Workflow File
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
tools:
  github:
---

# Daily Repo Status Report
Create a daily status report for maintainers.
Include
- Recent repository activity (issues, PRs, discussions, releases, code changes)
- Progress tracking, goal reminders and highlights
- Project status and recommendations
- Actionable next steps for maintainers
Keep it concise and link to the relevant issues/PRs.
```

## Integration with Agent Skills (Future Bridging)
Currently, `commands/*.md` in our plugin ecosystem map either to interactive IDE slash commands or to GitHub Models (`.prompt.yml`). 

Because GitHub Agentic Workflows require explicit GitHub Actions trigger contexts (`on:` frontmatter), they should be treated as a distinct class of integrations. If creating an Agentic Workflow, developers should consider using the `create-legacy-command` or a new specialized scaffolder to lay down the exact Markdown/YAML pair in the `.github/agentic-workflows/` directory, bypassing the generic interactive `agent-bridge`.

## Alternative Pattern: Smart Failures (Agentic DevOps)
While GitHub Agentic Workflows (above) refer to a specific platform feature by GitHub Next, developers can achieve similar "Shift Left" Continuous AI directly in standard GitHub Actions today using the **GitHub Copilot CLI** and the **Smart Failures** pattern.

This pattern uses an AI Agent to review non-deterministic rules (e.g., "Is this SQL query secure?", "Does this meet Acceptance Criteria?") and break the CI/CD build if rules are violated.

### The Smart Failure Architecture
A closed-loop system requiring three components:
1. **The Brain:** The GitHub Copilot CLI (`npm i -g @github/copilot`) installed on the runner.
2. **The Persona (System Prompt):** A standard markdown specification file (e.g., stored in `.github/agents/` or as an open standard Agent Skill in `.github/skills/`) defining instructions and a highly specific **"Kill Switch"** phrase that the AI must output if a failure condition is met.
3. **The Trigger (GitHub Action):** A bash script that executes the CLI, saves the output, and greps for the Kill Switch phrase to exit with a non-zero status.

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
