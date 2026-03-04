# Procedural Fallback Tree: Agent Bridge

If the bridge scripts fail or produce unexpected results, execute the following triage steps in order.

## 1. Target Directory Not Found
If `bridge_installer.py` reports that the target directory (`.agent/`, `.claude/`, etc.) does not exist:
- **Action**: Do NOT create the directory automatically. Print the exact `mkdir` command needed and wait for the user to confirm before creating it. A missing directory may indicate an uninitialised project.

## 2. Plugin Not Found
If `bridge_installer.py` cannot locate the specified plugin path:
- **Action**: Do NOT scan the filesystem for similar-named plugins. Report the error and list available plugins in the `plugins/` directory. Ask the user to confirm the correct plugin name.

## 3. Partial Bridge (Some Files Failed)
If the bridge completes but reports some files were skipped or failed to write:
- **Action**: Report each failed file individually with its error. Do NOT claim success. Offer to retry individual components once the user has resolved the reported issue (e.g., permissions).

## 4. `--target auto` Attempted
If any command or workflow attempts to use `--target auto`:
- **Action**: STOP immediately. This is explicitly prohibited. Ask the user to specify their exact environment (e.g., `antigravity`, `claude`, `gemini`, `github`). Never run with `--target auto`.
