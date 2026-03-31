---
description: >-
  Run the full agent system update: refresh all plugin code and redeploy
  capabilities to all agent environments.
args:
  dry_run:
    description: "Preview what would change without modifying files."
    type: boolean
---

# Update Agent System

Runs the master sync to update all plugins and redeploy capabilities to all agent environments.

```bash
if [ "${dry_run}" = "true" ]; then
    python3 ./plugins/plugin-manager/scripts/plugin_add.py --all -y --dry-run
else
    python3 ./plugins/plugin-manager/scripts/plugin_add.py --all -y
fi
```

> For full control over each step, invoke the `plugin-maintenance` skill.
