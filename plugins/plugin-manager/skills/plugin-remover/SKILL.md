---
name: plugin-remover
plugin: plugin-manager
description: Interactively select and uninstall agent plugins and skills from the local .agents/ environment.
allowed-tools: Bash, Read, Write
---

# Plugin Remover

Safely uninstalls plugins from agent environments and synchronizes tracking registries.

## Quick Start

### 1. Interactive Removal (Recommended)
Launch the interactive removal menu:
```bash
python3 scripts/plugin_remove.py
```

### 2. Headless Specific Removal
Remove a specific plugin without prompting:
```bash
python3 scripts/plugin_remove.py --plugins <plugin-name> --yes
```

### 3. Full Cleanup (Remove All)
Remove all tracked plugins and clean orphaned artifacts:
```bash
python3 scripts/plugin_remove.py --all --yes
```

## Progressive Disclosure & References

- **CLI Reference & Cleanup Protocol**: See `references/remover-cli-guide.md` for registry scrubbing rules and orphan cleanup behavior.
- **Acceptance Criteria**: See `references/acceptance-criteria.md` for structural invariants.
