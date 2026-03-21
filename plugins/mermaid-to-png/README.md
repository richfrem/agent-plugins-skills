# mermaid-to-png Plugin

Generated via Agent Scaffolder.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install mermaid-to-png
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/mermaid-to-png
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/mermaid-to-png

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install mermaid-to-png
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/mermaid-to-png
```

## Purpose
Converts Mermaid Markdown diagrams into high resolution PNG images.

## Directory Structure

```text
mermaid-to-png/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── convert-mermaid/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── convert.py
│       │   └── verify_png.py
│       └── references/
└── README.md
```

## Plugin Components

### Skills
- `convert-mermaid`

### Scripts
- `scripts/convert.py`
- `scripts/verify_png.py`

