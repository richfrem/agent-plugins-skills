
# Plugin Architecture & Bridge Process

**Author**: Antigravity Architect
**Version**: 2.0 (Dual Bridge)

## Overview

The agent bridge Architecture uses a **Dual Bridge** system to manage configuration. This ensures that the core system rules (Kernel) remain stable while allowing for flexible extension (Plugins).

### 1. The Kernel (System Bridge)
**Source**: `.kittify/memory` (Rules), `.windsurf/workflows` (Core Workflows)
**Tool**: `speckit_system_bridge.py`
**Responsibility**:
-   Syncs the **Constitution** and **Global Rules**.
-   Generates the **Monolithic Context Files** (`CLAUDE.md`, `GEMINI.md`, `copilot-instructions.md`).
-   Ensures all agents share the same "Brain" (Memory).

### 2. The Extensions (Plugin Bridge)
**Source**: `plugins/` (Individual Tool Capabilities)
**Tool**: `bridge_installer.py` (Plugin Manager)
**Responsibility**:
-   Installs specific **Skills** (e.g., `dependency-analysis`).
-   Deploys granular **Commands** (e.g., `/codify-form`).
-   Converts Markdown workflows into Agent-specific formats (TOML for Gemini, Prompts for Copilot).

---

## Execution Sequence

When setting up a fresh environment or updating the system, follow this sequence:

### Step 1: Initialize Kernel (System Sync)
Run this first to establish the ground rules and memory.
```bash
python plugins/spec-kitty/skills/spec-kitty-agent/scripts/speckit_system_bridge.py
```
> **Outcome**: Updates `.agent/rules`, `CLAUDE.md`, `copilot-instructions.md`.

### Step 2: Propagate Core Workflows (Spec Kitty Sync)
Run this to bridge the gap between `.windsurf` (CLI Init) and the Plugin System.
```bash
python plugins/spec-kitty/skills/spec-kitty-agent/scripts/sync_workflows.py
```
> **Outcome**: Copies fresh workflows from `.windsurf` to `plugins/spec-kitty/commands`.

### Step 3: Install Capabilities (Plugin Manager)
Run this to deploy all tools and commands to the agents.
```bash
python plugins/plugin-mapper/skills/plugin-mapper/scripts/install_all_plugins.py
```
> **Outcome**: Deploys `plugins/*` to `.agent/workflows`, `.github/prompts`, `.[target]/commands`, etc.

---

## Architecture Diagram

![Process Diagram](./agent_bridge_diagram.mmd)

