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
| **Plugin Commands** | `plugins/*/commands/*.md` | `bridge-plugin` skill (`plugin-manager`) | TOML Wrapping (Gemini) / Actor Swapping |
| **Plugin Skills** | `plugins/*/skills/*/` | `bridge-plugin` skill (`plugin-manager`) | Target Directory Projection |
| **Plugin Resources** | `plugins/*/resources/` | `bridge-plugin` skill (`plugin-manager`) | Contextual Linking |
