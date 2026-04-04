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
---

# Symlink Manager — Cross-Platform Skill

## The Core Problem

Git symlinks break across platforms because:

| Issue | macOS/Linux | Windows |
|---|---|---|
| Git setting | `core.symlinks=true` (default) | `core.symlinks=false` (default, unless Dev Mode enabled) |
| Link type | `ln -s` symlink | NTFS symlink *or* Junction Point |
| Permissions | Any user | Requires Developer Mode **or** admin elevation |
| Git behaviour | Stores as symlink object | Stores as plain text file containing the target path |

When `core.symlinks=false`, Git checks out a symlink as a **plain text file** whose contents are the target path. When you then `git pull` on the other machine, that text file arrives instead of a real link — silent, no error.

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

### Step 3 — Create symlinks with the script

Always use `scripts/symlink_manager.py` rather than raw `os.symlink()` because it:
1. Detects OS and chooses the right link strategy
2. Falls back to NTFS Junction Points on Windows when symlinks are unavailable
3. Writes a `symlinks.json` manifest so links can be re-created after a `git reset --hard`
4. Validates targets exist before linking
5. Optionally commits the manifest to the repo

```bash
# Create a single symlink
python ./scripts/symlink_manager.py create --src configs/shared.cfg --dst app/shared.cfg

# Re-create ALL links from the manifest
python ./scripts/symlink_manager.py restore

# Audit: list broken or missing links
python ./scripts/symlink_manager.py audit

# Full diagnosis of the environment
python ./scripts/symlink_manager.py diagnose
```

### Step 4 — Commit the manifest

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

Read `references/troubleshooting.md` when the user reports specific error messages.

---

## Output Conventions

- Always show the user the **diagnose output** before making changes
- When creating links, print a table: Source → Target, Type (symlink/junction/hardlink), Status ✓/✗
- When restoring from manifest, report counts: X created, Y skipped (already exist), Z failed
- On failure, always print the OS error and the recommended fix
