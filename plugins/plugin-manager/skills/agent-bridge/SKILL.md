---
name: agent-bridge
description: >
  Adapts and installs standard .claude-plugin structures into active agent
  environments (Antigravity, GitHub Copilot, Gemini, Claude Code). Trigger
  when deploying a plugin to a target IDE or agent environment.
allowed-tools: Bash, Read
---

# Agent Bridge

## Overview
This skill adapts plugin content into the specific formats required by different AI agents. While `plugin-replicator` moves the source code, `agent-bridge` ensures the runtime environment (Copilot, Gemini, etc.) can actually *see* and *use* the tools.

## Usage

### Deploy to Runtime Environment
Run the bridge installer to inject plugin capabilities into the target agent configuration folders.

```bash
# Auto-detect environment and install
python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin <plugin-path> --target auto

# Force install for GitHub Copilot
python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin <plugin-path> --target github
```

**Example:**
```bash
python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/guardian-onboarding --target github
```

> **Note**: The bridge installer is provided by the `plugin-mapper` plugin, which supports 30+ target environments including Cursor, Roo, Codex, and more.

## Supported Environments
*   **Antigravity** (`.agent/`): transforms commands for `.agent/workflows`.
*   **GitHub Copilot** (`.github/`): converts commands to `.prompt.md` files.
*   **Gemini** (`.gemini/`): wraps commands in TOML format.
*   **Claude Code** (`.claude/`): native slash-command format.
*   **Universal Generic**: any `--target <name>` creates `.<name>/` automatically.

## When to use
*   When you want your Claude plugins to be available in another IDE.
*   When deploying to a Gemini or Copilot environment.
*   When updating agent configurations after adding a new plugin.
