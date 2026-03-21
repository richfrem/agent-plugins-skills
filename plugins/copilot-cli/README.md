# Copilot CLI Plugin

GitHub Copilot CLI sub-agent system for persona-based analysis. Pipes large contexts to Copilot models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install copilot-cli
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/copilot-cli
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/copilot-cli

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install copilot-cli
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/copilot-cli
```

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to GitHub Copilot CLI. The skill manages prompt construction, persona injection, and output handling for headless Copilot CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **copilot-cli-agent** | Dispatch persona-based analysis tasks to Copilot CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Copilot model context without access to agent tools or memory.

## Structure

```
copilot-cli/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest
+-- skills/
|   +-- copilot-cli-agent/
|       +-- SKILL.md       # Core sub-agent dispatcher skill
+-- README.md
```

## Plugin Components

### Skills
- `copilot-cli-agent`

### Prerequisites
- `copilot` CLI installed and authenticated (`copilot login`)
