---
concept: dependency-management-plugin
source: plugin-code
source_file: dependency-management/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.552715+00:00
cluster: plugin-code
content_hash: f88657fbf6a35517
---

# Dependency Management Plugin 💊

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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



## See Also

- [[dependency-management-guide]]
- [[python-dependency-management-guide]]
- [[dependency-management-policy-detailed-reference]]
- [[dependency-management]]
- [[procedural-fallback-tree-dependency-management]]
- [[memory-management-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `dependency-management/README.md`
- **Indexed:** 2026-04-17T06:42:09.552715+00:00
