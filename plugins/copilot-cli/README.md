# Copilot CLI Plugin

GitHub Copilot CLI sub-agent system for persona-based analysis. Pipes large contexts to Copilot models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

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
