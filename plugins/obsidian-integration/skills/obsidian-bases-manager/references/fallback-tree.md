# Procedural Fallback Tree: Obsidian Bases Manager

## 1. Malformed YAML in Base File
If `./bases_ops.py` reports a YAML parse error:
- **Action**: Report the error with line number. Do NOT attempt auto-repair. Ask user to restore from backup. Never write to a Base file with corrupt YAML.

## 2. Row Index Out of Bounds
If `update-cell` is called with a row index that doesn't exist:
- **Action**: Run `./bases_ops.py read` to show current row count. Report the valid index range. Do NOT silently create a new row at the requested index.

## 3. ruamel.yaml Import Fails
If `import ruamel.yaml` raises `ImportError`:
- **Action**: Do NOT fall back to standard yaml or json. Report the missing dependency: `pip install ruamel.yaml`. Halt all Base file operations until resolved.
