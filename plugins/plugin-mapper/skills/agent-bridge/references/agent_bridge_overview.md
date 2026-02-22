
# Plugin Architecture & Bridge Process

**Author**: Spec Kitty Architect
**Version**: 2.0 (Dual Bridge)

## Overview

The Project Sanctuary Agent Architecture uses a **Dual Bridge** system to manage configuration. This ensures that the core system rules (Kernel) remain stable while allowing for flexible extension (Plugins).

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
python plugins/plugin-mapper/skills/agent-bridge/scripts/install_all_plugins.py
```
> **Outcome**: Deploys `plugins/*` to `.agent/workflows`, `.github/prompts`, etc.

---

## Architecture Diagram

![Process Diagram](./process_diagram.mmd)

```mermaid
flowchart TD
    subgraph Source_Truth [Source of Truth]
        Windsurf[".windsurf/workflows (Core Workflows)"]
        Kittify[".kittify/memory (Rules/Context)"]
        Plugins["plugins/ (Extensions/Tools)"]
    end

    subgraph Bridges [Bridge System]
        SB[System Bridge (Kernel)]
        PM[Plugin Bridge (Extensions)]
    end

    subgraph Agents [Target Environments]
        Antigravity[".agent/"]
        Copilot[".github/"]
        Claude[".claude/"]
        Gemini[".gemini/"]
    end

    %% Flows
    Windsurf -->|Ingest Core| SB
    Kittify -->|Ingest Rules| SB
    
    SB -->|Sync Rules & Context| Antigravity
    SB -->|Sync Rules & Context| Copilot
    SB -->|Sync Rules & Context| Claude
    SB -->|Sync Rules & Context| Gemini

    Plugins -->|Install Capabilities| PM
    
    PM -->|Deploy Skills & Commands| Antigravity
    PM -->|Deploy Prompts| Copilot
    PM -->|Deploy Commands| Claude
    PM -->|Deploy Commands| Gemini
```
