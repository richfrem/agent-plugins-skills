---
description: >
  Clean up orphaned artifacts left behind by plugins that have been removed
  from plugin-sources.json (uninstalled or deleted from source).
args:
  dry_run:
    description: "Preview what would be deleted without making changes."
    type: boolean
---

# Cleanup Orphaned Plugins

Identifies plugins tracked in `plugin-sources.json` that no longer have a valid source, and removes their lingering artifacts (skills, rules, workflows, hooks) from all agent directories.

> **Safety**: Only deletes artifacts for plugins explicitly removed via `plugin_remove.py` or absent from `plugin-sources.json`. Never touches custom project files.

```bash
echo "Running orphan cleanup analysis..."

if [ "${dry_run}" = "true" ]; then
    python plugins/plugin-manager/scripts/sync_with_inventory.py --cleanup-only --dry-run
else
    python plugins/plugin-manager/scripts/sync_with_inventory.py --cleanup-only
fi
```

> For a full sync (reinstall all tracked + cleanup removed), use the `/plugin-manager:update` command.
> To interactively select and remove plugins, use `plugin_remove.py` directly.
