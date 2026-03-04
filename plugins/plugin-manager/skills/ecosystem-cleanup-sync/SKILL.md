---
name: ecosystem-cleanup-sync
description: >
  Master synchronization and garbage collection skill. Synchronizes the local plugins against the vendor inventory.
  It safely cleans up orphaned artifacts from deleted plugins AND installs/updates all active plugins to the agent runtime environments (`.agent`, `.claude`, etc.).
---

# Ecosystem Cleanup & Sync 🧹🚀

This skill guides the process of synchronizing your local `plugins/` directory with all agent execution environments (`.agent`, `.claude`, `.github`, `.gemini`). It implements a "Safe Sync" approach: it deletes artifacts for vendor plugins you've removed, processes any new installs, and updates all existing code, while **project-specific** custom plugins are **never** deleted.

## Key Resources
- **Script**: `plugins/plugin-manager/scripts/sync_with_inventory.py`
- **Inventory Generator**: `plugins/plugin-manager/scripts/plugin_inventory.py`
- **Logic Guide**: `plugins/plugin-manager/resources/cleanup_process.md`
- **Visual Flow**: `plugins/plugin-manager/resources/cleanup_flow.mmd`

## The Core Rule
**"Only delete things that originated in .vendor. NEVER delete project-local unique plugins, skills, or workflows."**

## Execution Protocol

Do not immediately generate bash commands. Instead, operate as an interactive assistant using the following human-in-the-loop phases:

### Phase 1: Guided Discovery Interview
When the user invokes this skill, ask:
1. **Sync Mode:** "Do you want to run a safe DRY RUN to preview changes first, or APPLY the changes directly?" (Strongly suggest Dry Run for the first pass).
2. **Troubleshooting Prep:** Ask if they are aware of any specifically deleted or newly cloned plugins they expect to see synced.

### Phase 2: Recap-Before-Execute
Once variables are gathered, literally state what you are about to do and ask for confirmation. Use this format:

```markdown
### Proposed Sync Task
- **Operation**: Ecosystem Cleanup & Vendor Synchronization
- **Mode**: [Dry Run (Preview Only) / Execute (Modify Files)]
- **Constraint**: Local/Custom plugins will not be touched.

> Does this look correct? I will generate the bash commands once you confirm.
```

### Phase 3: Command Generation
Wait for the user's explicit confirmation (`yes`, `looks good`, `ok`). Once confirmed, generate the exact bash command according to their choices:

#### For Preview Mode (Dry Run)
```bash
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run
```

#### For Execution Mode (Apply)
```bash
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
