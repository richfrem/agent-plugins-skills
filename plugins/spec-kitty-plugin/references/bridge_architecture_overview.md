# Bridge Architecture Overview

## 1. Context: Unified Plugin Architecture
**InvestmentToolkit** utilizes a **Unified Plugin Architecture** for systematic AI agent interaction.
-   **Upstream Source**: The `plugins/` directory contains portable agent modules (Workflows, Skills, Scripts, Rules).
-   **Role**: Plugins provide the functional capabilities (e.g., `spec-kitty`, `database-tools`, `linter-rules`), while the project code resides in the target application's standard source directories (e.g., `src/`, `app/`, `legacy-system/`).

The **Bridge System** acts as the "Universal Adapter," projecting plugin capabilities and project-specific rules into the native formats required by specific AI tools (Antigravity, Gemini, Copilot, Claude).

## 2. Key Principles (from `AGENTS.md`)
-   **Bring Your Own Agent (BYOA)**: Any developer can use their preferred assistant (Antigravity, Gemini, Copilot, Claude) and still access the same workflows and rules.
-   **Single Source of Truth**: `plugins/<name>/` (Capabilities) and `.agent/rules/` (Project Rules) are the masters.
-   **One-Way Sync**: Changes flow *from* the Source of Truth *to* the agent directories. Agent directories are ephemeral build artifacts.
-   **Security**: Agent directories (`.claude/`, `.gemini/`, `.github/copilot/`) must **NEVER** be committed to Git.
-   **Pathing**: All paths in documentation/prompts must be absolute or relative to project root.

## 3. The Dual-Bridge Components

### A. Universal Rule/Workflow Sync (`spec-kitty-sync-plugin` skill)
This skill ensures the Project Constitution and Core workflows are synchronized across all agents.
1.  **Constitution Positioning**: Pulls `docs/constitution.md` (Version 4.2) and projects it to the TOP of all agent configuration files (e.g., `GEMINI.md`, `CLAUDE.md`).
2.  **Rule Integration**: Injects project-specific rules (`.agent/rules/`) into a dedicated block within the agent configurations, ensuring NO constitution duplication in the synced block.
3.  **Core Workflows**: Projects master workflows from `.windsurf/workflows/` to `.agents/workflows/spec-kitty/`.

### B. Plugin Bridge Installer (`bridge-plugin` skill in `plugin-manager`)
This skill manages the installation of standalone plugins into agent environments.
1.  **Command Projection**: Maps `plugins/*/commands/*.md` to plugin-specific subdirectories (e.g., `.agents/workflows/{plugin}/`, `.claude/commands/`).
2.  **Skill Integration**: Copies `plugins/*/skills/` to the canonical agent skills directory (`.agents/skills/`).
3.  **Transformation**: Performs actor swapping and agent-specific wrapping (e.g., Gemini TOML).

## 4. Automation & Workflows
-   **Usage (Rules/SDD)**: Trigger the `spec-kitty-sync-plugin` skill to sync project rules and constitution across agents.
-   **Usage (Plugins)**: Trigger the `bridge-plugin` skill (in `plugin-manager`) to install a specific plugin into agent environments.
-   **Batch Install**: Trigger `maintain-plugins` skill to install all plugins at once.

## 5. Visual Representation
See `plugins/spec-kitty/docs/bridge_process.mmd` for a detailed process diagram.
