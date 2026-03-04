---
name: plugin-maintenance
description: >
  Audits, synchronizes, and maintains the health of the plugin ecosystem.
  Handles structural compliance checks, agent environment sync (install + cleanup orphans),
  and README scaffolding. Trigger when validating new plugins, syncing plugins to agent
  configs, or performing routine ecosystem health checks.
allowed-tools: Bash, Write, Read
---

# Plugin Maintenance

## Overview
This skill is the ecosystem health hub. It covers three distinct operations:
- **Audit** — structural compliance checking against Open Standards
- **Sync** — keep agent environments (`.agent`, `.claude`, `.gemini`, `.github`) in sync with `plugins/`, cleaning up orphaned artifacts from deleted plugins
- **README** — scaffold missing documentation

**Core constraint**: Custom, project-specific plugins are NEVER deleted during sync. Only vendor-managed plugins that have been locally removed are cleaned up.

## References
- Sync process guide: `plugins/plugin-manager/skills/plugin-maintenance/references/cleanup_process.md`
- Sync flow diagram: `plugins/plugin-manager/skills/plugin-maintenance/references/cleanup_flow.mmd`

---

## Execution Protocol

> **CRITICAL**: Do not immediately generate bash commands. Operate as an interactive assistant using the following human-in-the-loop phases.

### Phase 1: Guided Discovery

When invoked, ask what operation the user needs:

```
Which maintenance operation?
1. [Audit]  — Check all plugins against structural standards
2. [Sync]   — Sync plugins/ to all agent environments (install + cleanup orphans)
3. [README] — Scaffold missing README.md files from plugin metadata
```

### Phase 2: Recap-Before-Execute

Once the user selects an operation, state exactly what you are about to do and ask for confirmation:

```markdown
### Proposed Maintenance Task
- **Operation**: [Audit / Sync (Dry Run) / Sync (Apply) / README Generation]
- **Target**: [All plugins / Specific plugin]
- **Impact**: [Read-only / Modifies agent config directories]

> Does this look correct? I will generate the commands once you confirm.
```

**For Sync**: Always propose a Dry Run first, then ask if the user wants to Apply.

### Phase 3: Command Execution

Wait for explicit confirmation (`yes`, `looks good`, `ok`), then run:

#### [Audit] Structural Compliance Check
Checks: presence of `skills/` directory, `SKILL.md` in every folder, absence of deprecated top-level `scripts/`.
```bash
python3 plugins/plugin-manager/scripts/audit_structure.py
```
> For deeper semantic checks, invoke the `ecosystem-standards` skill from `agent-skill-open-specifications`.

#### [Sync] Preview Changes (Dry Run — Always Run First)
```bash
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run
```

#### [Sync] Apply Changes
```bash
python3 plugins/plugin-manager/scripts/sync_with_inventory.py
```

#### [README] Generate Missing Documentation
```bash
python3 plugins/plugin-manager/scripts/generate_readmes.py --apply
```

### Phase 4: Verification

After any sync operation:
1. Check `local-plugins-inventory.json` (generated in project root) for current installed state.
2. Confirm custom plugins (not in the vendor list) are still present in `plugins/`.
3. Confirm artifacts for removed vendor plugins are cleaned from `.agent`, `.gemini`, etc.

---

## Escalation Taxonomy

| Condition | Response |
|-----------|----------|
| "Vendor directory not found" | Clone vendor: `git clone https://github.com/richfrem/agent-plugins-skills.git .vendor/agent-plugins-skills` |
| Custom plugin accidentally cleaned | STOP. Restore from `git checkout -- plugins/<name>/`. Never re-run sync until cause is identified. |
| `audit_structure.py` returns warnings | Read each warning. Do not suppress. Fix structural issues before bridging. |

---

## When to Use
- **After adding a new plugin** — run Audit to verify correct setup
- **After removing a vendor plugin** — run Sync to clean orphaned agent artifacts
- **Periodically** — to catch drift from accidental file placements
- **Before a release** — to ensure clean distribution state

## Next Actions
- Run the `agent-bridge` skill from `plugin-mapper` to deploy updated plugins to agent environments.
