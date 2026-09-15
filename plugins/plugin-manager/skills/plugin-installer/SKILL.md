---
name: plugin-installer
plugin: plugin-manager
description: >-
  Installs plugin components (skills, commands, workflows, rules, hooks, MCP)
  into the .agents/ central store and symlinks them to agent environments (.claude/, .gemini/, etc.).
  Trigger when a user says "install plugin", "deploy plugin", "add plugin", or "install from GitHub".
allowed-tools: Bash, Write, Read
---

# Plugin Installer

Deploys agent plugins and skills into the `.agents/` central store and symlinks them across agent environments.

Each install writes `.agents/ownership/<plugin>.json` as a desired-state manifest.
The manifest lists every source component and gives it a `should_install` flag.
An explicit `plugin-add <plugin>` re-enables every component in that plugin and
updates the manifest flags to `true`. The sync workflow uses an internal
preserve-ownership mode, so running sync does not silently re-enable components
that the user disabled.

## Quick Start

### 1. Interactive Installation (Recommended)
Launch the interactive multiselect menu:
```bash
python3 scripts/plugin_add.py
```

### 2. Install from GitHub or Local Path
```bash
# From GitHub repository shorthand
python3 scripts/plugin_add.py <owner/repo>

# From local directory with skill customization
python3 scripts/plugin_add.py plugins/ --select-skills
```

### 3. Non-Interactive / CI Installation
```bash
python3 scripts/plugin_add.py plugins/ --all -y
```

An explicit install of an already-registered plugin resets that plugin's
ownership entries to `should_install: true`. Edit the ownership manifest and
run `plugin-sync` when you want to preserve disabled selections.

## Progressive Disclosure & References

- **CLI Reference & Flags**: See `references/installer-cli-guide.md` for full parameter options and multi-IDE mappings.
- **Architecture & Ecosystem**: See `references/plugin_installer_overview.md` for the bridge pattern and central repository design.
- **Acceptance Criteria**: See `references/acceptance-criteria.md` for structural invariants.
- **Fallback Procedures**: See `references/fallback-tree.md` for environmental and network recovery trees.
