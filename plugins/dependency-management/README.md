# Dependency Management Plugin 💊

Python dependency management with pip-compile locked-file workflow for multi-service or monorepo python backends.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install dependency-management
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/dependency-management
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/dependency-management

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install dependency-management
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/dependency-management
```

## Core Rules
1. No manual `pip install` — use `.in` → `pip-compile` → `.txt`
2. Commit `.in` + `.txt` together
3. Core → Service-specific → Dev-only tiered hierarchy
4. Dockerfiles: only `COPY` + `pip install -r`

## Structure
```
dependency-management/
├── .claude-plugin/plugin.json
├── skills/dependency-management/
│   ├── SKILL.md
│   └── references/
└── README.md
```

## Plugin Components

### Skills
- `dependency-management`

