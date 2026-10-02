---
name: plugin-remover
plugin: plugin-manager
description: Interactively select and uninstall agent plugins and skills from the local .agents/ environment.
allowed-tools: Bash, Read, Write
---

# Plugin Remover (plugin-remover)

Safely uninstalls plugins from agent environments and synchronizes tracking registries.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: Dedicated to uninstalling plugins. For installing or refreshing plugins, use `plugin-installer` or `plugin-syncer`.
- **Dual Manifest Scrubbing**: Reads both legacy `artifacts` lists and ownership manifests to ensure complete removal of enabled and disabled assets.
- **Destructive Action Safety**: Never remove untracked project files outside `.agents/` and registered environment symlinks.
- **Confirmation Prompts**: Prompt for confirmation before wholesale deletion unless `--yes` is explicitly specified.

## Quick start

```bash
# Interactive removal menu
python3 plugins/plugin-manager/scripts/plugin_remove.py

# Remove a specific plugin non-interactively
python3 plugins/plugin-manager/scripts/plugin_remove.py --plugins <plugin-name> --yes

# Remove all tracked plugins and clean orphaned artifacts
python3 plugins/plugin-manager/scripts/plugin_remove.py --all --yes
```

## Workflow

1. **Phase 1: Target Identification**: Select targeted plugin(s) interactively or pass `--plugins <name>` arguments.
2. **Phase 2: Inventory Resolution**: Consult `.agents/ownership/<plugin>.json` and `.agents/plugin-sources.json` to map all deployed artifacts.
3. **Phase 3: Artifact & Symlink Pruning**: Delete target environment symlinks (`.claude/`, `.gemini/`) and purge files in `.agents/`.
4. **Phase 4: Registry Reconciliation**: Remove plugin entries from `plugin-sources.json` and delete the ownership manifest.

## Verification

```bash
# Verify no broken symlinks remain
python3 plugins/dev-utils/scripts/symlink_manager.py audit

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-remover --mode source
```

## References
- [remover-cli-guide.md](references/remover-cli-guide.md) - Removal flags, orphan pruning behavior, and registry scrubbing rules.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Uninstallation invariants and safety requirements.
- [fallback-tree.md](references/fallback-tree.md) - Fallback procedures and error recovery trees.
