---
description: Clean up orphaned artifacts from deleted plugins.
args:
  dry_run:
    description: "Run in dry-run mode to see what would happen without deleting files."
    type: boolean
---

# Cleanup Plugins

This command identifies plugins that have been removed from the local `plugins/` directory but still have lingering artifacts (skills, rules, workflows) in agent paths. It safely removes these orphans.

> **Safety Note:** This checks the Vendor Inventory. It ONLY deletes artifacts for plugins that originated from the vendor. Project-specific plugins are protected.

```bash
echo "Running cleanup analysis..."

if [ "${dry_run}" = "true" ]; then
    python plugins/plugin-manager/scripts/sync_with_inventory.py --cleanup-only --dry-run
else
    python plugins/plugin-manager/scripts/sync_with_inventory.py --cleanup-only
fi
```
