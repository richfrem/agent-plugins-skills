---
name: plugin-maintenance
description: >
  Audits and maintains the health of the plugin ecosystem. Verifies directory
  structure compliance, generates documentation, and flags legacy artifacts.
  Trigger when validating new plugins or performing routine ecosystem health checks.
allowed-tools: Bash, Write, Read
---

# Plugin Maintenance

## Overview
This skill provides tools for keeping plugins clean and compliant with official structural standards. It catches drift, legacy artifacts, and structural issues before they cause problems.

## Usage

### 1. Audit Structure
Check all plugins in the repository against the plugin structure guidelines.

```bash
python3 plugins/plugin-manager/scripts/audit_structure.py
```

**Checks Performed:**
- Presence of `skills/` directory.
- Presence of `SKILL.md` in every skill folder.
- Absence of deprecated top-level `scripts/` (for standard plugins).
- Compliance with file naming conventions.

> For a deeper content-level audit (YAML frontmatter, anti-patterns, line limits), invoke the `ecosystem-standards` skill from `agent-skill-open-specifications`.

### 2. Sync Plugins (Inventory-Based)
Synchronize the local `plugins/` directory with the upstream `.vendor` collection.

```bash
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run
python3 plugins/plugin-manager/scripts/sync_with_inventory.py
```

**Process:**
1. Generates vendor and local inventory comparison.
2. Identifies removed plugins (present in Vendor but not Local).
3. Cleans artifacts from `.agent`, `.github`, `.gemini`, `.claude`.
4. Re-installs/updates all currently installed plugins.

> **Note**: Project-specific plugins (not in Vendor) are always preserved.

### 3. Generate READMEs
Scaffold missing README.md files from plugin metadata.

```bash
python3 plugins/plugin-manager/scripts/generate_readmes.py --apply
```

## When to use
- **After adding a new plugin**: run audit to verify correct setup.
- **Periodically**: to catch drift or accidental file placements.
- **Before a release**: to ensure clean distribution state.
