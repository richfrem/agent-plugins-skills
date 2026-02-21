# Agent Scaffolders Plugin

Generated via Agent Scaffolder.

## Purpose
This plugin provides an active suite of code-generation tools to build Claude-compliant plugins seamlessly based on the `plugin-dev` official open standards set by Anthropic.

## Acknowledgments
We would like to give special recognition to the official Anthropic plugin repository as an important source of inspiration and foundational standards for this project:
- [Anthropic Claude Plugins Official Repository](https://github.com/anthropics/claude-plugins-official)
- [Official Plugin-Dev Toolkit](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev)

## Directory Structure

```text
agent-scaffolders/
├── .claude-plugin/
│   └── plugin.json       # Plugin manifest and routing definitions
├── skills/               # Directory containing Agent Skills (prompt logic)
├── agents/               # Directory containing Sub-Agent definitions
├── commands/             # Slash commands defined as Markdown frontmatter files
├── hooks/
│   └── hooks.json        # Agent lifecycle hook subscriptions
│   └── scripts/          # Event validation scripts
├── lsp.json              # Language Server Protocol definitions
├── .mcp.json             # Model Context Protocol integrations
├── README.md             # This documentation file
└── agent-scaffolders-architecture.mmd # Mermaid visual architecture diagram
```
