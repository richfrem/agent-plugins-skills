---
concept: symlink-troubleshooting-reference
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/symlink-manager/references/troubleshooting.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.253763+00:00
cluster: cause
content_hash: 36e0fb86ff7b5c84
---

# Symlink Troubleshooting Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Symlink Troubleshooting Reference

## Error: "A required privilege is not held by the client"

**Cause**: Windows requires elevated permissions or Developer Mode to create symlinks.

**Fix A — Enable Developer Mode (recommended, no reboot needed):**
1. Settings → System → For Developers
2. Toggle "Developer Mode" ON
3. Then re-run: `python scripts/symlink_manager.py restore`

**Fix B — Run as Administrator:**
Right-click PowerShell/Terminal → "Run as administrator", then run the script.

**Fix C — Use junction/hardlink fallback:**
The script falls back automatically if symlinks fail. Junctions work for directories without admin rights on older Windows. Note: junctions only work within the same drive.

---

## Error: Git checks out symlinks as plain text files

**Symptom**: After `git pull` on Windows, files like `app/config` contain text like `../shared/config` instead of being actual links.

**Cause**: `git config core.symlinks` is `false`.

**Fix:**
```powershell
# Step 1: Enable symlink support
git config core.symlinks true

# Step 2: Re-checkout all files with symlinks honoured
git rm --cached -r .
git reset --hard
```

Then run:
```bash
python scripts/symlink_manager.py restore
```

---

## Error: "Too many levels of symbolic links"

**Cause**: Circular symlink — A → B → A.

**Fix**: Run `python scripts/symlink_manager.py audit` and look for circular entries. Remove the cycle with `remove` command.

---

## Symlink shows as "? regular file (not a link)" in audit

**Cause**: Either:
1. Git checked it out as a text file (core.symlinks=false case), or
2. A previous failed restore left a partial file behind.

**Fix:**
```bash
git config core.symlinks true
git checkout -- <path-to-file>
# or
python scripts/symlink_manager.py restore
```

---

## macOS: "Operation not permitted" on network drives or APFS encrypted volumes

**Cause**: Some macOS volume configurations restrict symlinks.

**Fix**: Move your repo to a standard local APFS volume (~/Developer is a good location).

---

## Symlinks work locally but break on CI (GitHub Actions / GitLab CI)

**Cause**: CI runners often run as limited users, or Windows runners have `core.symlinks=false`.

**Fix**: Add to your CI workflow (GitHub Actions example):
```yaml
- name: Configure Git symlinks
  run: git config core.symlinks true
  shell: bash

- name: Restore symlinks
  run: python scripts/symlink_manager.py restore
```

For Windows runners, also add:
```yaml
- name: Enable Developer Mode equivalent
  run: |
    reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" /t REG_DWORD /f /v "AllowDevelopmentWithoutDevLicense" /d 1
  shell: cmd
```

---

## Checking if a path is a junction on Windows

```powershell
# PowerShell
(Get-Item "path\to\link").LinkType   # returns "Junction", "SymbolicLink", or $null

# cmd
fsutil reparsepoint query path\to\link
```

---

## The symlinks.json manifest is not being committed to git

Make sure it's not in `.gitignore`. The manifest should be tracked so teammates can run `restore` on fresh checkouts.

```bash
git add symlinks.json
git commit -m "chore: add symlink manifest"
```

---

## After git pull, some links break but others don't

**Cause**: Mixed `core.symlinks` history — some commits were made with it true, others false.

**Fix**: Standardize with `.gitattributes`:
```
# Force Git to always treat these as symlinks
*.link  -text
```

And add to `README` or `CONTRIBUTING.md`:
```
## Setup
Run `python scripts/symlink_manager.py restore` after cloning or pulling.
```


## See Also

- [[optimizer-engine-patterns-reference-design]]
- [[project-setup-reference-guide]]
- [[optimizer-engine-patterns-reference-design]]
- [[troubleshooting]]
- [[analysis-framework-reference]]
- [[path-reference-auditor---usage-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/symlink-manager/references/troubleshooting.md`
- **Indexed:** 2026-04-17T06:42:10.253763+00:00
