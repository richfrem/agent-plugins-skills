# Gemini CLI Plugin

Google Gemini CLI sub-agent system for persona-based analysis. Pipes large contexts to Gemini models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to Gemini CLI. The skill manages prompt construction, persona injection, and output handling for headless Gemini CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **gemini-cli-agent** | Dispatch persona-based analysis tasks to Gemini CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Gemini model context. Supports model selection via the `-m` flag (e.g., `gemini-3.1-flash-lite-preview`, `gemini-3-flash-preview`).

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
