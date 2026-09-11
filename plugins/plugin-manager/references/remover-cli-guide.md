# Plugin Remover CLI & Architecture Guide

## CLI Reference

### plugin_remove.py
```bash
python3 plugins/plugin-manager/scripts/plugin_remove.py [OPTIONS]
```
- `--all`: Remove all installed plugins and scrub all untracked artifacts in `.agents/`.
- `--plugins <p1,p2>`: Comma-separated list of plugins to uninstall.
- `--yes`, `-y`: Non-interactive mode, skip confirmation prompts.
- `--dry-run`: Preview removals without modifying filesystem.

## What Removal Does

1. **Artifact Removal**:
   - Deletes all components recorded in `.agents/ownership/<plugin>.json`.
   - Cleans target links in `.agents/skills/`, `.agents/workflows/`, `.claude/`, `.gemini/`, `.github/`.
2. **Registry Cleanup**:
   - Removes uninstalled plugins from `plugin-sources.json`.
   - Removes uninstalled skills from `skills-lock.json`.
   - Removes plugin entries from `plugin-retention.json`.
3. **Orphan Scrubbing**:
   - When all plugins are removed or `--all` is specified, any untracked or retired artifacts in `.agents/skills/` are purged so the directory is guaranteed 100% clean.
