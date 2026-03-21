# Obsidian Integration Plugin 💎

Bridge the gap between programmatic AI agent workflows and the local Obsidian knowledge base.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install obsidian-integration
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/obsidian-integration
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/obsidian-integration

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install obsidian-integration
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/obsidian-integration
```

## Dependencies

The `obsidian-vault-crud` and `obsidian-bases-manager` skills require `ruamel.yaml` for lossless YAML round-trip parsing:

```bash
pip install -r requirements.txt
# or: pip install ruamel.yaml
```

## Overview
Provides a suite of skills allowing LLM agents to safely perform CRUD operations on Obsidian Vaults, parse proprietary Obsidian Markdown (Wikilinks, block refs, callouts), traverse the connection graph, and manipulate dynamic visual views like Bases and Canvas.

## Core Capabilities
| Skill | Purpose |
| :--- | :--- |
| **obsidian-vault-crud** | Safe read/write/delete operations with atomic locks. |
| **obsidian-markdown-mastery** | Enforces strict parsing of proprietary Obsidian syntax. |
| **obsidian-canvas-architect** | Programmatically creates JSON Canvas (.canvas) files. |
| **obsidian-graph-traversal** | Analyzes wikilink connections to traverse the graph index. |
| **obsidian-bases-manager** | Reads and manipulates dynamic Obsidian Bases (.base) files. |

## Structure
- `skills/`: Core integration rules and capabilities.
- `.claude-plugin/`: Plugin manifest and runtime dependencies.

## Usage
These skills are invoked autonomously by the agent whenever a task involves reading, updating, or organizing information within the targeted Obsidian Vault directory.

## Plugin Components

### Skills
- `obsidian-init`
- `obsidian-vault-crud`
- `obsidian-markdown-mastery`
- `obsidian-canvas-architect`
- `obsidian-graph-traversal`
- `obsidian-bases-manager`

### Scripts
- `obsidian-parser/parser.py`

