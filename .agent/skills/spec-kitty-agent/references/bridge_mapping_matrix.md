# Bridge Mapping Matrix

This document outlines how files from the **Source of Truth** (Plugins & Project Rules) are transformed and mapped to each target AI agent.

## Sources
1.  **Project Rules**: `.agent/rules/*.md` (e.g., `constitution.md`)
2.  **Project Workflows**: `.windsurf/workflows/*.md` (e.g., `spec-kitty.accept.md`)
3.  **Plugin Capabilites**: `plugins/<name>/` (Commands, Skills, Resources)

## Mapping Table

| Artifact | Source Path | Target Bridge | Transformation |
| :--- | :--- | :--- | :--- |
| **Project Rules** | `.agent/rules/*.md` | `speckit_system_bridge.py` | Concatenation (Constitution Top + Rule Block) |
| **Project Workflows** | `.windsurf/workflows/*.md` | `speckit_system_bridge.py` | Actor Swapping + Command Patching |
| **Plugin Commands** | `plugins/*/commands/*.md` | `bridge_installer.py` | TOML Wrapping (Gemini) / Actor Swapping |
| **Plugin Skills** | `plugins/*/skills/*/` | `bridge_installer.py` | Target Directory Projection |
| **Plugin Resources** | `plugins/*/resources/` | `bridge_installer.py` | Contextual Linking |
