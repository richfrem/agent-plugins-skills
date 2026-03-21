# Coding Conventions Plugin 📝

Coding standards and header templates for Python, TypeScript/JavaScript, and C#/.NET.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install coding-conventions
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/coding-conventions
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/coding-conventions

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install coding-conventions
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/coding-conventions
```

## Templates Included
- `skills/coding-conventions-agent/assets/templates/python-tool-header-template.py` — Extended Python header
- `skills/coding-conventions-agent/assets/templates/js-tool-header-template.js` — JS/TS header

## Structure
```
coding-conventions/
├── .claude-plugin/plugin.json
├── skills/coding-conventions-agent/
│   ├── SKILL.md
│   ├── assets/templates/
│   │   ├── python-tool-header-template.py
│   │   └── js-tool-header-template.js
│   └── references/
└── README.md
```

## Acknowledgments
We align with the open ecosystem driving this architecture:
- [Agent Skills Open Standard (agentskills.io)](https://agentskills.io/)
- [Anthropic Claude Plugins Official Repository](https://github.com/anthropics/claude-plugins-official)
- [Microsoft Skills Repository](https://github.com/microsoft/skills)

## Plugin Components

### Skills
- `coding-conventions-agent`

### Dependencies
- `tool-inventory`

