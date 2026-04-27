---
name: plugin-remover
plugin: plugin-manager
description: Interactively select and uninstall agent plugins and skills from the local .agents/ environment.
---

# Plugin Remover Skill

## Overview

This skill orchestrates the safe, interactive removal of plugins from the local agent environment and updates the canonical tracking registries (`plugin-sources.json` and `skills-lock.json`).

By relying on the `plugin_remove.py` TUI, this skill ensures that no ghost files, orphaned symlinks, or stale hook registrations remain after a plugin is uninstalled.

## Key Architecture Rules

- **Execution**: All deletions must be run transparently through `plugin_remove.py`. Do NOT attempt to manually `rm -rf` plugin directories directly from `.agents/`.
- **Target Folders**: Artifacts are automatically scrubbed from `.agents/skills`, `.agents/workflows`, `.claude/`, `.gemini/`, etc.
- **Registries**: The uninstaller automatically parses and scrubs the removed plugin from both `skills-lock.json` and `plugin-sources.json` to keep auto-update loops synchronized.

## Instructions

Whenever the user asks to "remove a plugin", "uninstall a skill", or "delete a plugin", guide them to use the interactive TUI or run headless via flags.

### Remove via GitHub (remote, no local clone required)

```bash
# Interactive TUI — lists all plugins tracked in plugin-sources.json
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove

# Headless: remove a specific plugin without prompting
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove --plugins agent-loops --yes

# Headless: remove all tracked plugins
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove --all --yes
```

### Remove via Local Path (development / offline)

```bash
# Interactive TUI from local clone
uvx --from . plugin-remove

# Headless: remove a specific plugin
uvx --from . plugin-remove --plugins agent-loops --yes

# Or run the underlying Python script directly:
python plugins/plugin-manager/scripts/plugin_remove.py
python plugins/plugin-manager/scripts/plugin_remove.py --plugins agent-loops --yes
python plugins/plugin-manager/scripts/plugin_remove.py --dry-run
```

### What Removal Does

For each selected plugin, the uninstaller:
1. Deletes the plugin directory/files from `.agents/skills/`, `.agents/workflows/`, `.agents/agents/`, `.agents/hooks/`, `.claude/`, `.gemini/`, etc.
2. Removes the plugin entry from `plugin-sources.json` (auto-update registry).
3. Removes the plugin entry from `skills-lock.json`.

## Dependencies

- Python 3.8+ (No external pip dependencies required).
- `plugin-sources.json` must exist and contain tracked plugins. Run `plugin-add` first.

