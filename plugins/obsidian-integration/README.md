# Obsidian Integration Plugin 💎

Bridge the gap between programmatic AI agent workflows and the local Obsidian knowledge base.

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
