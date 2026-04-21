# Acceptance Criteria: plugin-remover

## Functional Requirements
1. **Targeted Deletion**: The skill must interactively or programmatically trigger `plugin_remove.py`.
2. **Ghost Pruning**: The skill must ensure all `.agents/`, `.claude/`, and `.gemini/` environments are completely purged of the selected plugin's artifacts.
3. **Registry Maintenance**: Must cleanly scrub the targeted plugins from both `plugin-sources.json` and `skills-lock.json`.

## Non-Functional Requirements
1. **Safety**: Never run raw `rm -rf` operations inside the `.agents/` environment outside of the heavily vetted deletion logic of `plugin_remove.py`.
2. **Multi-Source Support**: Must intelligently group uninstallation views via source-keys when used interactively.
