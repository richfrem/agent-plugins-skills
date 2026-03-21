# Procedural Fallback Tree: Obsidian Init

## 1. Obsidian App Not Installed
If `ls /Applications/Obsidian.app` fails:
- **Action**: Report explicitly that the Obsidian desktop app is required. Provide the Homebrew install command. Do NOT proceed with vault init until the user confirms Obsidian is installed.

## 2. Target Directory Has No Markdown Files
If `../scripts/init_vault.py` reports zero `.md` files found:
- **Action**: Report the finding and ask the user to confirm they want to initialize an empty vault. Do NOT silently create `.obsidian/` in an unintended directory.

## 3. `.gitignore` Write Permission Denied
If updating `.gitignore` fails with `PermissionError`:
- **Action**: Report the permission failure. Print the lines that should be added manually. Do NOT skip the gitignore update silently — unexpectedly committed `.obsidian/` config causes conflicts.

## 4. `--validate-only` Shows Failures
If validation reports missing `.obsidian/` config but the user asked for validate-only:
- **Action**: Report findings clearly but make NO changes. If user then asks to fix, run a new session with the init command (without `--validate-only`).
