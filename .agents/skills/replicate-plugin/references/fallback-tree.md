# Procedural Fallback Tree: Plugin Replicator

If the replication scripts fail or produce unexpected results, execute the following triage steps in order.

## 1. Source Plugin Not Found
If `plugin_replicator.py` exits with code 1 stating the source path does not exist:
- **Action**: Do NOT attempt to locate it by scanning the filesystem. Report the error and list the available plugins in the source directory. Ask the user to confirm the correct plugin name or path.

## 2. Destination Project Not Found
If the destination path does not exist:
- **Action**: Do NOT create the destination directory chain silently. Report that the target project directory was not found and ask the user to verify the path. Creating an empty directory structure could mask a mistyped path.

## 3. Symlink Creation Failed (--link mode)
If `symlink_to()` raises a `PermissionError` or `OSError`:
- **Action**: Report the failure. On macOS/Linux, suggest checking directory permissions. On Windows, note that Developer Mode or Administrator privileges may be required. Offer to fall back to copy mode (`--link` removed).

## 4. Partial Copy Detected (interrupted run)
If a previous run was interrupted and the destination is in an inconsistent state:
- **Action**: Do NOT assume the state is correct. Recommend running with `--clean --dry-run` first to review what a full clean sync would change. Let the user decide whether to apply it.
