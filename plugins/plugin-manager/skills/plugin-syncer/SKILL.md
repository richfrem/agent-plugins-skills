---
name: plugin-syncer
plugin: plugin-manager
description: >
  Synchronizes the agent environments. Looks at the inventory (plugin-sources.json) 
  and reinstalls all skills and plugins from the sources indicated. Also cleans up 
  any orphaned artifacts from removed plugins. Trigger when the user asks to "sync 
  plugins", "update all plugins", "refresh environment", or "run the sync script".
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only.

---
# Plugin Syncer

Synchronizes all plugins managed by `plugin-sources.json`. It will sequentially install/update all registered plugins from their designated sources (GitHub or local directories), and then automatically prune any orphaned capabilities left by removed plugins.

## Execution Protocol

Run the sync script:

```bash
python ./scripts/sync_with_inventory.py
```

> **Dry Run Mode**: If the user wants to preview without executing, use:
> `python ./scripts/sync_with_inventory.py --dry-run`

> **Cleanup Only**: If the user only wants to clean orphans without reinstalling, use:
> `python ./scripts/sync_with_inventory.py --cleanup-only`

## Rules Merge Safety

`sync_with_inventory.py` reinstalls every registered plugin via `plugin_installer.py`,
including each plugin's `rules/` into `.agent/rules/`. This is a **merge, not an
overwrite**: `deploy_rules()` diff-merges the plugin's `rules/<name>.md` into any
existing `.agent/rules/<name>.md`, preserving newer/downstream content the plugin
source doesn't yet have. If a full sync doesn't seem to have updated a rule you
expected to change, check whether `.agent/rules/` already had newer content than
`plugins/<plugin>/rules/<name>.md` — the plugin source itself needs updating, since
sync will keep preserving the newer downstream version on every future run.
