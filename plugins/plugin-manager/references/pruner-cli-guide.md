# Component Retention Pruner CLI Guide

## Commands

### Interactive Mode (TUI)
```bash
python3 plugins/plugin-manager/scripts/prune_installed_skills.py --interactive
```
- Arrow keys (`↑`/`↓`): navigate components.
- `Space`: toggle retention for current item.
- `a`: toggle all items in current view.
- `/`: filter components by search term.
- `Enter`: confirm and advance to next plugin / execution plan.
- `q`: quit without applying changes.

### Headless Dry-Run (Plan Only)
```bash
python3 plugins/plugin-manager/scripts/prune_installed_skills.py --dry-run
```
Calculates pruning plan from `plugin-retention.json` and prints removable components without deleting any files.

### Headless Execution
```bash
python3 plugins/plugin-manager/scripts/prune_installed_skills.py --execute --confirm-token PRUNE-INSTALLED-SKILLS
```
Requires explicit `--confirm-token PRUNE-INSTALLED-SKILLS` to delete files.
