---
name: plugin-syncer
plugin: plugin-manager
description: >-
  Synchronizes agent environments from plugin-sources.json. Reinstalls all plugins,
  cleans up orphaned artifacts, and enforces retention policies.
allowed-tools: Bash, Read, Write
---

# Plugin Syncer

Synchronizes all plugins registered in `plugin-sources.json` and enforces component retention.

## Quick Start

### 1. Run Synchronization
```bash
python3 scripts/sync_with_inventory.py
```

### 2. Preview Synchronisation (Dry Run)
```bash
python3 scripts/sync_with_inventory.py --dry-run
```

### 3. Cleanup Stale Artifacts Only
```bash
python3 scripts/sync_with_inventory.py --cleanup-only
```

## Progressive Disclosure & References

- **CLI Reference & Rules Merge Safety**: See `references/syncer-cli-guide.md` for rules merging, retention enforcement, and validation details.
- **Acceptance Criteria**: See `references/acceptance-criteria.md` for synchronization invariants.
