# Path Reference Auditor - Usage Guide

## Overview

Three-phase audit system to find and validate all file path references in plugins and skills.

## Phase 1: SCAN - Find All References

```bash
python3 ./path_reference_auditor.py --project . --phase scan
```

**What it does:**
- Walks all `plugins/`, `.agents/skills/`,  `.claude/skills/` directories
- Finds every `./reference` pattern in `.py`, `.md`, `.mmd`, `.json`, `.sh` files
- Extracts file path, line number, reference string
- Saves to `inventory.json` (raw, unverified)

**Output:**
```
📂 Phase 1: SCAN - Finding all file references...
  ✓ Scanned 94 files
  ✓ Found 156 references
  ✓ Inventory saved: inventory.json
```

## Phase 2: VERIFY - Check Each Reference

```bash
python3 ./path_reference_auditor.py --project . --phase verify
```

**What it does:**
- Reads `inventory.json`
- For each reference, checks if it exists in the skill/plugin directory
- Tries multiple resolution paths (relative to source, skill, parent dirs)
- Detects symlinks and broken symlinks
- Updates inventory with status information

**Output:**
```
✓ Phase 2: VERIFY - Checking if references exist...
  ✓ Verified 156 references
  ✓ Inventory saved: inventory.json
```

## Phase 3: REPORT - Generate Analysis

```bash
# Summary (overview)
python3 ./path_reference_auditor.py --project . --phase report --report summary

# Missing files (broken references)
python3 ./path_reference_auditor.py --project . --phase report --report missing

# Broken symlinks
python3 ./path_reference_auditor.py --project . --phase report --report broken_symlinks

# All symlinks (working + broken)
python3 ./path_reference_auditor.py --project . --phase report --report symlinks

# All reports
python3 ./path_reference_auditor.py --project . --phase report --report all
```

**Example output:**
```
📊 Audit Summary:
  Files scanned: 94
  Total references: 156
  ✓ Valid: 150
  ❌ Missing: 4
  🔗 Symlinks: 12
  🔗 Broken symlinks: 2
```

## Skill Boundary Check

Flag references that point OUTSIDE a skill directory.

```bash
# All skills
python3 ./check_skill_boundaries.py inventory.json --batch all

# Single skill (by name)
python3 ./check_skill_boundaries.py inventory.json --skill adr-management

# Single skill (by path)
python3 ./check_skill_boundaries.py inventory.json --skill plugins/adr-manager/skills/adr-management
```

**Example violation:**
```
FILE: plugins/adr-manager/skills/adr-management/SKILL.md:45
  REF: ../../templates/adr-template.md
  SKILL ROOT: plugins/adr-manager/skills/adr-management/
  RESOLVES TO: plugins/adr-manager/templates/adr-template.md  ❌ OUTSIDE!
```

**Fix:** Create a symlink inside the skill:
```bash
cd plugins/adr-manager/skills/adr-management
mkdir -p templates
ln -s ../../templates/adr-template.md templates/adr-template.md
```

## Plugin Boundary Check

Flag references in plugin root that point OUTSIDE the plugin.

```bash
# All plugins
python3 ./check_plugin_boundaries.py inventory.json --batch all

# Single plugin (by name)
python3 ./check_plugin_boundaries.py inventory.json --plugin plugin-installer

# Single plugin (by path)
python3 ./check_plugin_boundaries.py inventory.json --plugin plugins/plugin-installer
```

**Example violation:**
```
FILE: plugins/adr-manager/commands/adr-management.md:8
  REF: .././architecture.md
  PLUGIN ROOT: plugins/adr-manager/
  RESOLVES TO: docs/architecture.md  ❌ OUTSIDE!
```

**Fix:** Copy or symlink into plugin:
```bash
cd plugins/adr-manager
cp ../../docs/architecture.md ./docs/
# or symlink
ln -s ../../docs ./docs
```

## Inventory Structure

After Phase 1 (SCAN), `inventory.json` contains:
```json
{
  "metadata": {
    "scanned_at": "2026-03-20T...",
    "verified_at": null,
    "project_root": "...",
    "total_files_scanned": 94,
    "total_references_found": 156,
    "phase": "scanned"
  },
  "references": [
    {
      "source_file": "plugins/adr-manager/skills/adr-management/SKILL.md",
      "reference": "./scripts/adr_manager.py",
      "line": 17,
      "status": null
    }
  ]
}
```

After Phase 2 (VERIFY), each reference has a status:
```json
{
  "status": {
    "exists": true,
    "type": "file",
    "path": "plugins/adr-manager/skills/adr-management/scripts/adr_manager.py",
    "resolved_path": "/full/path/..."
  }
}
```

## Status Types

| Type | Meaning | Action |
|------|---------|--------|
| `file` | Regular file exists | ✓ OK |
| `directory` | Directory exists | ✓ OK |
| `symlink` | Symlink exists and target exists | ✓ OK |
| `symlink (target: BROKEN)` | Symlink exists but target missing | ❌ Fix target |
| `missing` | File/symlink doesn't exist | ❌ Create it |

## Complete Workflow

```bash
# Step 1: Generate inventory
python3 ./path_reference_auditor.py --project . --phase scan

# Step 2: Verify all references
python3 ./path_reference_auditor.py --project . --phase verify

# Step 3: Generate reports
python3 ./path_reference_auditor.py --project . --phase report --report all

# Step 4: Check skill boundaries
python3 ./check_skill_boundaries.py inventory.json --batch all

# Step 5: Check plugin boundaries
python3 ./check_plugin_boundaries.py inventory.json --batch all

# Step 6: Fix violations and re-run checks
```

## Performance

- **Phase 1 (SCAN)**: ~30-60 seconds (scans all files)
- **Phase 2 (VERIFY)**: ~10-30 seconds (checks filesystem)
- **Phase 3 (REPORT)**: < 1 second (memory-based)

Run SCAN/VERIFY once, then REPORT many times without rescanning.

## Advanced: Query with jq

```bash
# Find all missing references
cat inventory.json | jq '.references[] | select(.status.exists == false)'

# Find all broken symlinks
cat inventory.json | jq '.references[] | select(.status.target == "BROKEN")'

# Count violations by source file
cat inventory.json | jq 'group_by(.source_file) | map({file: .[0].source_file, missing: [.[] | select(.status.exists == false)] | length})'

# Export to CSV
cat inventory.json | jq -r '.references[] | select(.status.exists == false) | [.source_file, .line, .reference] | @csv'
```
