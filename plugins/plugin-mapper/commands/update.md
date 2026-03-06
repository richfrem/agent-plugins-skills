---
description: Refresh agent capabilities and update plugins.
args:
  dry_run:
    description: "Run in dry-run mode to see what would happen without making changes."
    type: boolean
github-model-export: true
---

# Update / Refresh Plugins

```bash
# Refresh all plugins in all agent environments
python plugins/plugin-mapper/skills/agent-bridge/scripts/install_all_plugins.py
```

