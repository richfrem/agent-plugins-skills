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

Runs the master sync to update plugins and redeploy all agent capabilities.

```bash
if [ "${dry_run}" = "true" ]; then
    python3 ./scripts/sync_with_inventory.py --dry-run
else
    python3 ./scripts/update_agent_system.py
fi
```

> For full control over each step, invoke the `plugin-maintenance` skill.
