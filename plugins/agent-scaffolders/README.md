# Agent Scaffolders Plugin

Generated via Agent Scaffolder.

## Purpose
This plugin provides an active suite of code-generation tools to build Claude-compliant plugins seamlessly based on the `plugin-dev` official open standards set by Anthropic.

## Acknowledgments
We would like to give special recognition to the official Anthropic plugin repository as an important source of inspiration and foundational standards for this project:
- [Anthropic Claude Plugins Official Repository](https://github.com/anthropics/claude-plugins-official)
- [Official Plugin-Dev Toolkit](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev)

## Core Dependencies
This plugin relies heavily on the **Separation of Concerns** principle. It acts as the "Tool/Router" but relies on the `agent-skill-open-specifications` plugin as the "Source of Truth" for canonical standards. Therefore, to scaffold L4 skills, this plugin dynamically fetches constraints from:
- `plugins reference/agent-skill-open-specifications/L4-pattern-definitions/`

## Directory Structure


```text
agent-scaffolders/
```
agent-scaffolders/
├── .claude-plugin/plugin.json
├── README.md
├── references/
│   ├── hitl-interaction-design.md
│   └── pattern-decision-matrix.md
├── scripts/
│   ├── audit.py
│   └── scaffold.py
├── skills/
│   └── (12 scaffolder skills)
└── templates/
    └── (5 Jinja templating files)
```

## Plugin Components

### Skills
- `audit-plugin`
- `create-agentic-workflow`
- `create-azure-agent`
- `create-docker-skill`
- `create-github-action`
- `create-hook`
- `create-legacy-command`
- `create-mcp-integration`
- `create-plugin`
- `create-skill`
- `create-stateful-skill`
- `create-sub-agent`

### Scripts
- `skills/audit-plugin/scripts/audit.py`
- `scripts/scaffold.py`

### Dependencies
- `context-bundler`

