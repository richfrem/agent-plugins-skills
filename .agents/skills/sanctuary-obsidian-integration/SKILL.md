---
name: sanctuary-obsidian-integration
description: "Project Sanctuary-specific skill for managing the Obsidian vault as an external hippocampus. Knows the vault path, naming conventions, and integration patterns. Uses the generic obsidian-integration plugin."
---

# Sanctuary Obsidian Integration

**Status:** Active
**Domain:** Project Sanctuary
**Depends on:** `obsidian-integration` (generic vault CRUD, markdown parsing, canvas, graph traversal)

## Purpose

This skill is the **Sanctuary-specific glue layer** that knows how to use the generic `obsidian-integration` plugin for Project Sanctuary's Obsidian vault workflows.

The utility plugin is project-agnostic — it provides vault operations, markdown parsing, canvas creation, and graph traversal. This skill knows:
- Where the Sanctuary vault lives
- What naming conventions to use
- How to integrate Protocol 128 snapshots with the vault
- The vision for "External Hippocampus" (long-term AI memory via Obsidian)

## Vault Configuration

| Setting | Value |
|---|---|
| Vault path | Configured per deployment via `OBSIDIAN_VAULT_PATH` env var |
| Naming convention | `YYYY-MM-DD_<topic>.md` for notes |
| Exclusion filters | `.git/`, `node_modules/`, `.worktrees/` |

## Integration Patterns

### Session Notes → Vault
After Protocol 128 seal phase, key learnings can be exported as vault notes:

```bash
# Parse markdown to validate structure
python plugins/obsidian-integration/obsidian-parser/parser.py <file>

# CRUD operations for vault notes
# (use the obsidian-vault-crud skill from obsidian-integration)
```

### Canvas for Architecture Diagrams
Use the `obsidian-canvas-architect` skill to generate visual architecture canvases from Sanctuary's protocol and workflow diagrams.

### Graph Traversal for Knowledge Discovery
Use the `obsidian-graph-traversal` skill to find connections between learning snapshots, ADRs, and protocols in the vault.

## Cross-References

- **Vision**: `plugins/obsidian-integration/resources/vision-external-hippocampus.md`
- **Architecture**: `plugins/obsidian-integration/resources/architecture-background.md`
- **Safety**: `plugins/obsidian-integration/resources/safety-learnings.md`
