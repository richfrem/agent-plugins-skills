---
name: symlink-manager
description: >
  Create, audit, repair, and document cross-platform symlinks that work correctly
  on both Windows and macOS/Linux. Use this skill whenever the user mentions symlinks,
  symbolic links, junction points, .gitconfig symlinks, broken links after git pull,
  cross-platform path issues, or needs help with ln -s equivalents on Windows.
  Also trigger when the user reports that files are missing or wrong after switching
  between Mac and Windows machines using Git. This skill solves the common problem
  where symlinks committed on macOS show up as plain text files on Windows (and vice versa)
  because of Git's core.symlinks setting or missing Developer Mode / elevated permissions.
  **IMPORTANT FOR WINDOWS USERS:** Developer Mode must be enabled before creating symlinks.
  Without it, Git will check out symlinks as plain-text files or hardlinks, breaking cross-platform workflows.
---

# Symlink Manager — Cross-Platform Skill

## The Core Problem

Git symlinks break across platforms because:

| Issue | macOS/Linux | Windows |
|---|---|---|
| Git setting | `core.symlinks=true` (default) | `core.symlinks=false` (default, unless Dev Mode enabled) |
| Link type | `ln -s` symlink | NTFS symlink *or* Junction Point *or* Hardlink |
| Permissions | Any user | Requires Developer Mode **or** admin elevation |
| Git behaviour | Stores as symlink object | Stores as plain text file containing the target path |

When `core.symlinks=false`, Git checks out a symlink as a **plain text file** whose contents are the target path. When you then `git pull` on the other machine, that text file arrives instead of a real link — silent, no error.

### The Hardlink Trap

When `core.symlinks=false` and Developer Mode is disabled, symlinks can be accidentally replaced with **hardlinks**. Hardlinks **cannot be committed as symlinks to Git**, so they break the cross-platform workflow:

1. macOS user commits real symlinks (core.symlinks=true by default)
2. Windows user with Developer Mode off: symlinks checkout as plain-text files, then get replaced with hardlinks
3. Windows user pushes: Git sees plain-text file, commits it as a file, not a symlink
4. macOS user pulls: receives text file instead of symlink — broken

**Solution: Always use real symlinks, never hardlinks.** Enable Developer Mode on Windows first, then use `/create-sym-link` command to create proper symlinks that Git recognizes.

---

## Workflow

### Step 1 — Diagnose the environment

Run the diagnosis script first. It checks:
- OS and Python version
- `git config core.symlinks` (local + global)
- Whether Developer Mode is active (Windows)
- Whether the script is running as admin (Windows)
- Existing symlinks vs broken links vs text-file stand-ins in the repo

```bash
python ./scripts/symlink_manager.py diagnose
```

### Step 2 — Fix Git config

On **Windows** (needs Developer Mode enabled first, or run as admin):
```bash
git config core.symlinks true
git rm --cached -r .          # unstage everything
git reset --hard              # re-checkout with symlinks honoured
```

On **macOS / Linux** (usually already correct):
```bash
git config --get core.symlinks   # should say "true"
```

Add a `.gitattributes` line to lock symlinks in the repo:
```
* text=auto
*.symlink  -text
```

### Step 3 — Create symlinks (Automatic Platform Detection)

**For cross-platform teams: Use the Python script** — it automatically handles OS differences without requiring bash, PowerShell, or .sh scripts.

Use the `/create-sym-link` command in Claude Code for an interactive workflow:
```
/create-sym-link
```
This prompts for source and destination paths and uses the Python symlink manager.

Or use the Python script directly (works on Windows, macOS, and Linux):
```bash
# Create a single symlink (automatically detects OS)
python ./scripts/symlink_manager.py create --src plugins/plugin-manager/scripts/bridge_installer.py --dst plugins/plugin-manager/skills/plugin-installer/scripts/bridge_installer.py

# Re-create ALL links from the manifest
python ./scripts/symlink_manager.py restore

# Audit: list broken or missing links
python ./scripts/symlink_manager.py audit

# Full diagnosis of the environment
python ./scripts/symlink_manager.py diagnose
```

**The Python script automatically:**
- ✓ macOS/Linux: Creates true symlinks
- ✓ Windows with Developer Mode: Creates true symlinks
- ✓ Windows without Developer Mode: Falls back to junctions (dirs) or hardlinks (files)
- ✓ No external shell scripts needed — pure Python with standard library only

**Critical: If symlinks were created as hardlinks or plain-text files:**
1. Delete them: `rm plugins/plugin-manager/skills/*/scripts/bridge_installer.py`
2. Enable Developer Mode on Windows (Settings → System → For Developers)
3. Set git config: `git config core.symlinks true`
4. Use `/create-sym-link` command or `python ./scripts/symlink_manager.py create ...`
5. Commit: `git add -A && git commit -m "fix: replace hardlinks with proper symlinks"`

### Step 4 — Bulk Fix Symlinks in Folders

If you have multiple text-file stand-ins in a folder hierarchy, use the bulk fixer:

```bash
# Scan folder, generate inventory, and fix all broken symlinks
python ./scripts/bulk_symlink_fixer.py plugins/plugin-manager/skills/maintain-plugins/scripts
```

The bulk fixer:
- Scans the folder recursively for text-file stand-ins and broken symlinks
- Generates an inventory report (count and list of issues)
- Calls `symlink_manager.py create` in a loop to fix each one
- Reports summary (fixed, skipped, failed counts)

### Step 5 — Commit the manifest

Commit `symlinks.json` to the repo. On a fresh checkout (or after a `git pull` breaks links on Windows), any developer runs:
```bash
python ./scripts/symlink_manager.py restore
```
…and all links are recreated correctly for their platform.

---

## Windows-Specific Notes

- **Developer Mode** (Settings → System → For Developers) allows unprivileged symlink creation. Recommend enabling this for all devs on the team.
- Without Developer Mode, the script falls back to **Junction Points** for directories and **hardlinks** for files. This covers 90% of use-cases but junctions only work within the same volume.
- Running the script as Administrator bypasses the Developer Mode requirement entirely.
- Set `git config --global core.symlinks true` *after* enabling Developer Mode.

## macOS/Linux Notes

- Symlinks always work. The main risk is accidentally committing with `core.symlinks=false` inherited from a shared config.
- Run `git config --list --show-origin | grep symlinks` to see where the setting comes from.

---

## Reference Files

- `references/troubleshooting.md` — Common error messages and fixes
- `scripts/symlink_manager.py` — The cross-platform Python script
- `.agent/rules/symlink-cross-platform.md` — Repository-wide symlink best practices and requirements

Read `references/troubleshooting.md` when the user reports specific error messages.

---

## Output Conventions

- Always show the user the **diagnose output** before making changes
- When creating links, print a table: Source → Target, Type (symlink/junction/hardlink), Status ✓/✗
- When restoring from manifest, report counts: X created, Y skipped (already exist), Z failed
- On failure, always print the OS error and the recommended fix
