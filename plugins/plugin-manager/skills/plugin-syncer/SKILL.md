---
name: plugin-syncer
plugin: plugin-manager
description: >-
  Synchronizes agent environments from plugin-sources.json. Reinstalls all plugins,
  cleans up orphaned artifacts, and enforces retention policies.
allowed-tools: Bash, Read, Write
---

# Plugin Syncer

Synchronizes all plugins registered in `plugin-sources.json`, then enforces each
`.agents/ownership/<plugin>.json` desired-state manifest. Components marked
`"should_install": false` are removed; enabled components are restored by the
normal plugin installation pass.

Ownership manifests are intentionally formatted with one compact JSON line per
component, making it faster to change `should_install` values manually. The
manifest remains standard JSON and can be edited directly before running sync.

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
- **Fallback Procedures**: See `references/fallback-tree.md` for fallback and recovery trees.
