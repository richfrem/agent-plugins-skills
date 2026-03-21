# Gemini CLI Plugin

Google Gemini CLI sub-agent system for persona-based analysis. Pipes large contexts to Gemini models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install gemini-cli
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/gemini-cli
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/gemini-cli

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install gemini-cli
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/gemini-cli
```

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to Gemini CLI. The skill manages prompt construction, persona injection, and output handling for headless Gemini CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **gemini-cli-agent** | Dispatch persona-based analysis tasks to Gemini CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Gemini model context. Supports model selection via the `-m` flag (e.g., `gemini-2.5-pro`, `gemini-2.5-flash`).

## Structure

```
gemini-cli/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest
+-- skills/
|   +-- gemini-cli-agent/
|       +-- SKILL.md       # Core sub-agent dispatcher skill
+-- README.md
```

## Plugin Components

### Skills
- `gemini-cli-agent`

### Prerequisites
- `gemini` CLI installed and authenticated
