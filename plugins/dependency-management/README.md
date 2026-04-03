# Dependency Management Plugin 💊

Python dependency management with pip-compile locked-file workflow for multi-service or monorepo python backends.

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

