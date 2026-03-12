# mermaid-to-png Plugin

Generated via Agent Scaffolder.

## Purpose
Converts Mermaid Markdown diagrams into high resolution PNG images.

## Directory Structure

```text
mermaid-to-png/
├── .claude-plugin/
│   └── plugin.json       # Plugin manifest and routing definitions
├── skills/               # Directory containing Agent Skills (prompt logic)
├── agents/               # Directory containing Sub-Agent definitions
├── commands/             # Legacy commands and flat-file workflows
├── hooks.json            # Agent lifecycle hook subscriptions
├── lsp.json              # Language Server Protocol definitions
├── mcp.json              # Model Context Protocol integrations
├── README.md             # This documentation file
└── mermaid-to-png-architecture.mmd # Mermaid visual architecture diagram
```

## Plugin Components

### Skills
- `convert-mermaid`

### Scripts
- `scripts/convert.py`
- `scripts/verify_png.py`

