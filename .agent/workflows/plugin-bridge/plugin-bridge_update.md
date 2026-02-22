---
description: Refresh agent capabilities and update plugins.
args:
  dry_run:
    description: "Run in dry-run mode to see what would happen without making changes."
    type: boolean
---

# Update / Refresh Plugins

# 1. Update Bridges (Priority: Propagate Local Changes)
echo "Refreshing agent capabilities from local plugins..."
python plugins/plugin-mapper/scripts/install_all_plugins.py
```
