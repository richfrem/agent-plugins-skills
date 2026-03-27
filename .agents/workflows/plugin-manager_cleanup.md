---
description: >
  Clean up orphaned artifacts left behind by plugins that have been removed
  from the local plugins/ directory.
args:
  dry_run:
    description: "Preview what would be deleted without making changes."
    type: boolean
---

# Cleanup Orphaned Plugins

Identifies plugins removed from `plugins/` that still have lingering artifacts (skills, rules, workflows) in agent directories, and safely removes them.

> **Safety**: Only deletes artifacts for vendor-originated plugins. Project-specific custom plugins are never touched.

```bash
echo "Running orphan cleanup analysis..."

if [ "${dry_run}" = "true" ]; then
    python3 ./scripts/sync_with_inventory.py --dry-run
else
    python3 ./scripts/sync_with_inventory.py
fi
```

> For a full sync (install new + cleanup removed), use the `/plugin-manager:update` command.
