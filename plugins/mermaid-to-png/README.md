# mermaid-to-png Plugin

Generated via Agent Scaffolder.

## Installation
### Option 1: Skills Only (End Users)
```bash
npx skills add ./plugins/mermaid-to-png
```
This installs the skills from this plugin.

### Option 2: Full Deployment (Skills + Commands + Agents)
For complete access to all components, use the bridge-plugin skill:
```bash
# Use the bridge-plugin skill to deploy all components
# python ./plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/mermaid-to-png
```

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

