---
description: >-
  Run a full sync: reinstall all plugins tracked in plugin-sources.json from their
  registered sources, then clean up any stale artifacts from removed plugins.
args:
  dry_run:
    description: "Preview what would change without modifying files."
    type: boolean
---

# Update Agent System

Reads `plugin-sources.json` and redeploys all tracked plugins to all agent environments,
then prunes any orphaned artifacts left by removed plugins.

```bash
if [ "${dry_run}" = "true" ]; then
    python plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run
else
    python plugins/plugin-manager/scripts/sync_with_inventory.py
fi
```

> This command uses `plugin-sources.json` as the source of truth — only plugins
> registered there are synced. To add a new plugin, run `plugin_add.py` first.
