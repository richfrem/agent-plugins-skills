---
description: Update all installed plugins from the vendor collection.
args:
  dry_run:
    description: "Run in dry-run mode to see what would happen without making changes."
    type: boolean
---

# Update Plugins

This command updates all installed plugins with the latest code from the vendor repository and refreshes agent capabilities.

```bash
# 1. Update Vendor Source (Source of Truth)
if [ -d ".vendor/agent-plugins-skills" ]; then
    echo "Updating vendor repository..."
    cd .vendor/agent-plugins-skills
    git pull
    cd ../..
else
    echo "Error: Vendor repository not found at .vendor/agent-plugins-skills"
    exit 1
fi

# 2. Copy Updates (Vendor -> Local)
echo "Copying updates to local plugins..."
python plugins/plugin-manager/scripts/update_from_vendor.py

# 3. Running Sync (Update Agent Capabilities)
echo "Syncing inventory and capabilities..."
if [ "${dry_run}" = "true" ]; then
    python plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run
else
    python plugins/plugin-manager/scripts/sync_with_inventory.py
fi
```
