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

## Execution Protocol

Do not immediately generate bash commands. Instead, operate as an interactive assistant using the following human-in-the-loop phases:

### Phase 1: Guided Discovery
When the user invokes this skill, ask what type of maintenance they want to perform:
1. **[Audit]**: Check all plugins against structural standards (catches drift, legacy files, and missing SKILL files).
2. **[Sync]**: Synchronize the local `plugins/` directory with the upstream `.vendor` collection (identifies removed plugins and re-installs current ones).
3. **[README]**: Scaffold missing `README.md` files for plugins based on metadata.

### Phase 2: Recap-Before-Execute
Once the user selects an operation, summarize what you are about to do and ask for confirmation. Example:

```markdown
### Proposed Maintenance Task
- **Operation**: Structural Audit
- **Target**: Entire local ecosystem
- **Impact**: Read-only check

> Does this look correct? I will generate the exact commands once you confirm.
```

### Phase 3: Command Execution
Wait for the user's explicit confirmation (`yes`, `looks good`). Once confirmed, generate the exact bash command according to their choice:

#### For Structural Audit
**Checks Performed:** Presence of `skills/` directory, `SKILL.md` in every folder, absence of deprecated top-level `scripts/`.
```bash
python3 plugins/plugin-manager/scripts/audit_structure.py
```
> *For deeper content-level checks, remind the user to invoke `ecosystem-standards`.*

#### For Inventory Sync
**Checks Performed:** Compares vendor to local, cleans artifacts, reinstalls upstream code.
```bash
# First show what will change
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run
# Then execute
python3 plugins/plugin-manager/scripts/sync_with_inventory.py
```

#### For README Generation
```bash
python3 plugins/plugin-manager/scripts/generate_readmes.py --apply
```

## When to use
- **After adding a new plugin**: run audit to verify correct setup.
- **Periodically**: to catch drift or accidental file placements.
- **Before a release**: to ensure clean distribution state.
