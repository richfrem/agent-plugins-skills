---
name: plugin-bootstrap
description: |
  Initializes or updates the local plugin ecosystem from the central vendor repo.
  Use this when a project needs to pull the latest plugin code or initialize for the first time.
---

# Plugin Bootstrap Protocol

This skill provides a standardized way to initialize or update your local plugin environment from the central vendor repository.

## Automated Bootstrap

The quickest way to update your ecosystem is to run the bootstrap script:

```bash
python3 plugins/plugin-manager/scripts/plugin_bootstrap.py
```

This command will:
1. Ensure the vendor source in `.vendor/agent-plugins-skills` is present and up to date.
2. Refresh your local `plugins/` folder with the latest code.
3. Synchronize your active agent configurations (Antigravity, etc.).

---

## Manual Execution (Phase-by-Phase)

If you need more granular control, you can perform the bootstrap in stages:

### Phase 1: Ensure Vendor Source
If the `.vendor/agent-plugins-skills` directory is missing or needs a fresh update:

```bash
# Clone for the first time
mkdir -p .vendor
git clone https://github.com/richfrem/agent-plugins-skills.git .vendor/agent-plugins-skills

# OR update existing
cd .vendor/agent-plugins-skills && git pull
```

### Phase 2: Execute Update
Run the standardized update script to synchronize existing plugins in `plugins/`:

```bash
python3 plugins/plugin-manager/scripts/update_from_vendor.py
```

### Phase 3: Finalize Sync
Ensure all agent configurations (Antigravity, etc.) are updated to reflect the new code:

```bash
python3 plugins/plugin-manager/scripts/sync_with_inventory.py
```

---

## Next Steps (Local Environment Setup)

Once the bootstrap is complete, you may need to perform additional setup or maintenance:

1. **[Plugin Replicator](../plugin-replicator/SKILL.md)**: Install new plugins or replicate specific plugins to other project paths.
2. **[Inventory Sync](../inventory-sync/SKILL.md)**: Perform a deep audit and cleanup of your sync state.
3. **[Plugin Maintenance](../plugin-maintenance/SKILL.md)**: Audit the health and structure of your active plugins.
4. **[Agent Bridge](../agent-bridge/SKILL.md)**: Manually trigger resource synchronization for specific agent targets.
