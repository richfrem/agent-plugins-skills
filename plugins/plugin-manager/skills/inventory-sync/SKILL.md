---
name: inventory-sync
description: >
  Synchronizes local plugins from the vendor inventory, safely cleaning up
  deleted vendor plugins while preserving project-specific customizations.
  Trigger when updating the plugin ecosystem from an upstream vendor source.
---

# Inventory Sync

This skill guides the process of synchronizing a local plugin collection with the vendor's master inventory, implementing a "Safe Sync" approach that ensures vendor plugins are updated cleanly while **project-specific** plugins and artifacts are **never** deleted.

## Key Resources
- **Script**: `plugins/plugin-manager/scripts/sync_with_inventory.py`
- **Inventory Generator**: `plugins/plugin-manager/scripts/plugin_inventory.py`
- **Logic Guide**: `plugins/plugin-manager/resources/cleanup_process.md`
- **Visual Flow**: `plugins/plugin-manager/resources/cleanup_flow.mmd`

## The Core Rule
**"Only delete things that originated in .vendor. NEVER delete project-local unique plugins, skills, or workflows."**

## Usage

### 1. The Variance Check (Automatic)
The synchronization script compares:
1.  **Vendor Inventory** (`.vendor/.../vendor-plugins-inventory.json`): The upstream "menu" of available plugins.
2.  **Local Inventory**: A generated list of what is currently in `plugins/`.

### 2. How to Run Sync
```bash
# Preview changes without making them (recommended for first run)
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run

# Apply the sync
python3 plugins/plugin-manager/scripts/sync_with_inventory.py
```

### 3. Verification Steps
After syncing:
1. Check `local-plugins-inventory.json` (generated in root) for the current installed state.
2. Ensure custom plugins (not in the vendor list) are still present in `plugins/`.
3. Confirm artifacts for removed vendor plugins are gone from `.agent`, `.gemini`, etc.

## Troubleshooting

**"Vendor directory not found"** — Clone the vendor repo into `.vendor/agent-plugins-skills`. Without it, the script runs in Safety Mode (no cleanup).

**"I want to delete a vendor plugin"** — Delete the plugin folder from `plugins/`, then run `sync_with_inventory.py`. The script detects it as deleted and cleans up its artifacts.

**"I want to delete a local plugin"** — Delete from `plugins/` and manually remove its artifacts, as the script protects non-vendor items.
