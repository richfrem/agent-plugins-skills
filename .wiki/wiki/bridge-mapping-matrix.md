---
concept: bridge-mapping-matrix
source: plugin-code
source_file: spec-kitty-plugin/references/bridge_mapping_matrix.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.372592+00:00
cluster: project
content_hash: 72e2d6abf5e84923
---

# Bridge Mapping Matrix

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Bridge Mapping Matrix

This document outlines how files from the **Source of Truth** (Plugins & Project Rules) are transformed and mapped to each target AI agent.

## Sources
1.  **Project Rules**: `.agent/rules/*.md` (e.g., `constitution.md`)
2.  **Project Workflows**: `.windsurf/workflows/*.md` (e.g., `spec-kitty.accept.md`)
3.  **Plugin Capabilites**: `plugins/<name>/` (Commands, Skills, Resources)

## Mapping Table

| Artifact | Source Path | Target Bridge | Transformation |
| :--- | :--- | :--- | :--- |
| **Project Rules** | `.agent/rules/*.md` | `spec-kitty-sync-plugin` skill | Concatenation (Constitution Top + Rule Block) |
| **Project Workflows** | `.windsurf/workflows/*.md` | `spec-kitty-sync-plugin` skill | Actor Swapping + Command Patching |
| **Plugin Commands** | `plugins/*/commands/*.md` | `plugin-installer` skill (`plugin-manager`) | TOML Wrapping (Gemini) / Actor Swapping |
| **Plugin Skills** | `plugins/*/skills/*/` | `plugin-installer` skill (`plugin-manager`) | Target Directory Projection |
| **Plugin Resources** | `plugins/*/resources/` | `plugin-installer` skill (`plugin-manager`) | Contextual Linking |


## See Also

- [[improvement-mapping]]
- [[39-pattern-l4-architectural-decision-matrix]]
- [[39-pattern-l4-architectural-decision-matrix]]
- [[pattern-decision-matrix]]
- [[skill-ecosystem-mapping]]
- [[plugin-bridge-architecture-process]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/references/bridge_mapping_matrix.md`
- **Indexed:** 2026-04-17T06:42:10.372592+00:00
