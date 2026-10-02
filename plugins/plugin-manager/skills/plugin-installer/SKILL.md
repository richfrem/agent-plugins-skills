---
name: plugin-installer
plugin: plugin-manager
description: >-
  Installs plugin components (skills, commands, workflows, rules, hooks, MCP)
  into the .agents/ central store and symlinks them to agent environments (.claude/, .gemini/, etc.).
  Trigger when a user says "install plugin", "deploy plugin", "add plugin", or "install from GitHub".
  Only for adding a plugin that is not yet registered. For "sync", "resync" or refreshing
  existing plugins use plugin-syncer. Keeps .agents/ownership/ choices unless --enable-all is passed.
allowed-tools: Bash, Write, Read
---

# Plugin Installer (plugin-installer)

Deploys agent plugins and skills into the `.agents/` central store and symlinks them across agent environments.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: Dedicated to installing newly added plugins. For refreshing or syncing existing registered plugins, use `plugin-syncer`.
- **Ownership State Tracking**: Every install creates or updates `.agents/ownership/<plugin>.json` tracking component-level `should_install` desired states.
- **Preserve Disabled Selections**: Default installation respects existing user disables unless `--enable-all` is explicitly passed.
- **Direct Symlinks**: Symlinks generated into agent environments (`.claude/`, `.gemini/`) must link directly to `.agents/` store without symlink chaining.

## Quick start

```bash
# Interactive installation with multiselect menu
python3 plugins/plugin-manager/scripts/plugin_add.py

# Install all components non-interactively
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ --all -y
```

## Workflow

1. **Phase 1: Source Discovery**: Validate target source (local path or GitHub `owner/repo`) and inspect plugin manifest.
2. **Phase 2: Ownership Manifest Generation**: Record `.agents/ownership/<plugin>.json` defining enabled components and mapped artifacts.
3. **Phase 3: Central Store Provisioning**: Deploy assets into the `.agents/` central primitive directories.
4. **Phase 4: Agent Environment Symlinking**: Symlink deployed primitives into IDE-specific environments (`.claude/`, `.gemini/`).

## Verification

```bash
# Verify environment symlink health
python3 plugins/dev-utils/scripts/symlink_manager.py audit

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-installer --mode source
```

## References
- [installer-cli-guide.md](references/installer-cli-guide.md) - CLI parameters, flags, and multi-IDE mappings.
- [plugin_installer_overview.md](references/plugin_installer_overview.md) - Bridge pattern architecture and repository layout.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Structural invariants and verification checklist.
- [fallback-tree.md](references/fallback-tree.md) - Environmental recovery and fallback procedures.
