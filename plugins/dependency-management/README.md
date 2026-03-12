# Dependency Management Plugin 💊

Python dependency management with pip-compile locked-file workflow for multi-service or monorepo python backends.

## Installation
```bash
claude --plugin-dir ./plugins/dependency-management
```

## Passive Rules
| Rule | Description |
|:---|:---|
| `rules/dependency-management.mdc` | Automatically injects core dependency workflow constraints (like `.in` to `pip-compile`) when editing `requirements` or `Dockerfile` files. |

## Core Rules
1. No manual `pip install` — use `.in` → `pip-compile` → `.txt`
2. Commit `.in` + `.txt` together
3. Core → Service-specific → Dev-only tiered hierarchy
4. Dockerfiles: only `COPY` + `pip install -r`

## Structure
```
dependency-management/
├── .claude-plugin/plugin.json
├── rules/dependency-management.mdc
├── skills/dependency-management/SKILL.md
└── README.md
```

## Plugin Components

### Skills
- `dependency-management`

