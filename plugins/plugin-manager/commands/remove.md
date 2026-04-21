---
description: >-
  Interactively select and uninstall plugins. Wipes them from local agent environments
  (.agents/) and automatically deregisters them from plugin-sources.json.
args:
  plugin_name:
    description: "Specific plugin name to remove headlessly. Leave blank for interactive TUI."
    type: string
    required: false
---

# Remove Plugin

Safely uninstalls one or more plugins completely from all mapped agent environments and cleans up registers.

```bash
if [ -n "${plugin_name}" ]; then
    # Headless: remove a specific plugin
    python plugins/plugin-manager/scripts/plugin_remove.py --plugins "${plugin_name}" --yes
else
    # Interactive picker grouped by source
    python plugins/plugin-manager/scripts/plugin_remove.py
fi
```
