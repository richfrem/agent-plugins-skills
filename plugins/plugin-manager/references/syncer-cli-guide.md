# Plugin Syncer CLI & Architecture Guide

## CLI Reference

### sync_with_inventory.py
```bash
python3 plugins/plugin-manager/scripts/sync_with_inventory.py [OPTIONS]
```
- `--dry-run`: Preview synchronisation actions without modifying filesystem.
- `--cleanup-only`: Clean up orphaned or stale artifacts without reinstalling plugins.
- `--no-prune`: Skip automatic post-sync component retention enforcement.

## Synchronisation Protocol

1. **Registry Discovery**:
   - Reads `plugin-sources.json` for all tracked sources and plugins.
2. **Stale Cleanup**:
   - Detects and cleans up plugins whose local source directory no longer exists.
3. **Reinstallation**:
   - Executes `plugin_add.py` for each source to reinstall or update plugins.
4. **Retention Policy Enforcement**:
   - If `plugin-retention.json` is present and `--no-prune` is not passed, executes `prune_installed_skills.py --execute --confirm-token PRUNE-INSTALLED-SKILLS`.
5. **Post-Sync Validation**:
   - Verifies all artifacts and detects unexpected or missing directories.

## Rules Merge Safety

`deploy_rules()` diff-merges plugin rules into `.agent/rules/<name>.md`, preserving newer downstream edits. To force updates, update the plugin source repository.
