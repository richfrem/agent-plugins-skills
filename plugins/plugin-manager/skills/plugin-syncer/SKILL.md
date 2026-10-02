---
name: plugin-syncer
plugin: plugin-manager
description: >-
  Synchronizes agent environments from plugin-sources.json. Refreshes every registered
  plugin while honoring the should_install choices in .agents/ownership/, cleans up
  orphaned artifacts, and removes disabled components. This is what "sync", "resync",
  "plugin sync" and "update plugins" mean: run sync_with_inventory.py, never plugin_add.py.
allowed-tools: Bash, Read, Write
---

# Plugin Syncer (plugin-syncer)

Synchronizes registered plugins from `plugin-sources.json` while enforcing `.agents/ownership/` desired-state manifests.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Canonical Sync Tool**: Always run `sync_with_inventory.py` for "sync" or "resync" requests; never call `plugin_add.py`.
- **Preserve Ownership States**: Honoring `should_install: false` choices in `.agents/ownership/<plugin>.json` is strictly required; disabled components must not be resurrected.
- **Dry-Run Preview**: Preview proposed file modifications and symlink updates before executing live sync.
- **Orphan Pruning**: Stale or unreferenced symlinks pointing to disabled components must be cleaned automatically.

## Quick start

```bash
# Preview synchronization changes (dry-run)
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run

# Run full synchronization
python3 plugins/plugin-manager/scripts/sync_with_inventory.py

# Clean up stale artifacts only
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --cleanup-only
```

## Workflow

1. **Phase 1: Registry Scan**: Read `.agents/plugin-sources.json` and load ownership manifests from `.agents/ownership/`.
2. **Phase 2: Preview & Diff**: Execute with `--dry-run` to inventory additions, deletions, and component toggles.
3. **Phase 3: Component Synchronization**: Deploy enabled components to `.agents/` and remove assets marked `"should_install": false`.
4. **Phase 4: Multi-IDE Pruning & Audit**: Refresh symlinks across `.claude/` and `.gemini/` environments and audit link health.

## Verification

```bash
# Verify environment symlink health
python3 plugins/dev-utils/scripts/symlink_manager.py audit

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-syncer --mode source
```

## References
- [syncer-cli-guide.md](references/syncer-cli-guide.md) - Rules merging, retention enforcement, and validation details.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Synchronization invariants and safety requirements.
- [fallback-tree.md](references/fallback-tree.md) - Fallback procedures and recovery trees.
