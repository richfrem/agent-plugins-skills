---
trigger: manual
---

# Workflow Enforcement Policy

**Tool discovery details → `plugins/tool-inventory/skills/tool_discovery/SKILL.md`**
**Spec workflow details → `plugins/spec-kitty/skills/spec_kitty_workflow/SKILL.md`**

## Core Principle
All agent interactions MUST be mediated by **Slash Commands** (`.agent/workflows/*.md`). No bypassing with raw shell.

## Architecture (ADR-036: Thick Python / Thin Shim)

| Layer | Location | Purpose |
|:------|:---------|:--------|
| **Slash Commands** | `.agent/workflows/*.md` | User-facing interface |
| **Thin Shims** | `scripts/bash/*.sh` | Dumb wrappers that `exec` Python |
| **Tool Inventory** | `plugins/tool-inventory/skills/tool-inventory/scripts/query_cache.py` | Dispatches to orchestrator/tools |
| **Orchestrator** | `plugins/agent-loops/skills/orchestrator/` | Logic, enforcement, Git checks |

## Command Domains
- 🗄️ **Retrieve** — Fetching data (RLM, RAG)
- 🔍 **Investigate** — Deep analysis, mining
- 📝 **Codify** — Documentation, ADRs, contracts
- 📚 **Curate** — Maintenance, inventory updates
- 🧪 **Sandbox** — Prototyping
- 🚀 **Discovery** — Spec-Driven Development (Track B)

## Registration (MANDATORY after creating/modifying workflows or tools)
```bash
python plugins/tool-inventory/skills/tool-inventory/scripts/manage_tool_inventory.py add --path <path>
```

## Workflow File Standards
- **Location**: `.agent/workflows/[kebab-case-name].md`
- **Frontmatter**: `description`, `tier`, `track`
- **Shims**: No logic — only `exec` Python scripts
