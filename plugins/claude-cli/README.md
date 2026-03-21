# Claude CLI Plugin

Claude CLI sub-agent system for persona-based analysis. Pipes large contexts to Anthropic models for security audits, architecture reviews, QA analysis, and other specialized tasks requiring an isolated model context.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install claude-cli
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/claude-cli
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/claude-cli

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install claude-cli
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/claude-cli
```

## Overview

Provides a sub-agent dispatcher pattern for routing analysis tasks to Claude CLI. The skill manages prompt construction, persona injection, and output handling for headless Claude CLI invocations.

## Core Capabilities

| Skill | Purpose |
| :--- | :--- |
| **claude-cli-agent** | Dispatch persona-based analysis tasks to Claude CLI sub-agents |

## Usage

Invoke when specialized analysis (security audit, architecture review, QA) benefits from an isolated Claude model context. Particularly useful for large file analysis via stdin piping without loading content into the parent agent's memory.

## Structure

```
claude-cli/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest
+-- skills/
|   +-- claude-cli-agent/
|       +-- SKILL.md       # Core sub-agent dispatcher skill
+-- README.md
```

## Plugin Components

### Skills
- `claude-cli-agent`

### Prerequisites
- `claude` CLI installed and authenticated (`claude login`)
