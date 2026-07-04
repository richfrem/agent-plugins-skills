# Rule: Always Use symlink_manager.py for Symlink Operations

## Mandatory Protocol

**NEVER create symlinks with `ln -s` directly.**
**NEVER create real file copies where a symlink should exist.**

All symlink creation, repair, and auditing in this project MUST go through:

```
.agents/skills/symlink-manager/scripts/symlink_manager.py
```

---

## Required Workflow — Every Time You Touch Symlinks

### Step 1: Diagnose first
```bash
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
```
Read the output. Identify every `? regular file (not a link)` and `✗ broken symlink` before touching anything.

### Step 2: Remove real-file imposters
If a file that should be a symlink is a real file, delete it first:
```bash
rm -f path/to/real-file-that-should-be-symlink
```

### Step 3: Add new links to symlinks.json (the manifest)
```python
# Add entries via script, NOT by hand-editing symlinks.json:
# { "src": "canonical/source.py", "dst": "skill/scripts/source.py", "strategy": "symlink", "description": "..." }
```
The `src` must be the canonical master copy (in plugin root scripts/, references/, assets/).
The `dst` is the skill subfolder location.

### Step 4: Restore all from manifest
```bash
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore
```

### Step 5: Verify
```bash
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
```
Zero `? regular file` or `✗ broken symlink` entries must remain before committing.

---

## Canonical Source Locations (portfolio-advisor plugin)

| File | Canonical Master | All skills get a symlink |
|------|-----------------|--------------------------|
| `*.py` scripts | `plugins/portfolio-advisor/scripts/` | → `skills/<skill>/scripts/` |
| `investment_thesis.md` | `plugins/portfolio-advisor/references/` | → `skills/<skill>/references/` |
| `portfolio.json` | `investment_screener/frontend/src/data/` | → `skills/<skill>/references/` |
| `PortfolioAnalysisRecommendations.md` | `plugins/portfolio-advisor/assets/templates/` | → `skills/<skill>/assets/templates/` |

---

## ❌ Prohibited Actions

- ❌ `ln -s <src> <dst>` directly in shell (bypasses manifest, links won't be recreated on fresh checkout)
- ❌ Copying file contents into a skill subfolder instead of symlinking
- ❌ Editing symlinks.json by hand without running `restore` afterwards
- ❌ Committing without running `diagnose` to confirm zero broken/real-file issues

---

## Skill Reference

Read the full skill before any symlink work:
`.agents/skills/symlink-manager/SKILL.md`
