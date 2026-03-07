---
name: plugin-maintenance
description: >
  Audits, synchronizes, and maintains the health of the plugin ecosystem.
  Handles structural compliance checks against Open Standards, agent environment
  sync (install + cleanup orphans), and README scaffolding. Trigger when
  validating new plugins, syncing plugins to agent configs, or performing
  routine ecosystem health checks.
allowed-tools: Bash, Write, Read
---
# Plugin Maintenance

## Overview
This skill is the ecosystem health hub. It covers three operations:
- **Audit** — structural compliance checking against Open Standards
- **Sync** — keep agent environments in sync with `plugins/`, cleaning up orphaned artifacts
- **README** — scaffold missing documentation

**Core constraint**: Custom, project-specific plugins are NEVER deleted during sync. Only vendor-managed plugins that have been locally removed are cleaned up.

## References
- Sync process guide: `plugins/plugin-manager/skills/plugin-maintenance/references/cleanup_process.md`
- Sync flow diagram: `plugins/plugin-manager/skills/plugin-maintenance/references/cleanup_flow.mmd`

---

## Execution Protocol

> **CRITICAL**: Do not immediately generate bash commands. Operate as an interactive assistant.

### Phase 1: Guided Discovery

When invoked, ask what operation the user needs:

```
Which maintenance operation?
1. [Audit]  — Check plugin(s) against structural Open Standards
2. [Sync]   — Sync plugins/ to all agent environments (install + cleanup orphans)
3. [README] — Scaffold missing README.md files from plugin metadata
```

### Phase 2: Recap-Before-Execute

State exactly what you are about to do and ask for confirmation:

```markdown
### Proposed Maintenance Task
- **Operation**: [Audit / Sync (Dry Run) / Sync (Apply) / README Generation]
- **Target**: [All plugins / Specific plugin: name]
- **Impact**: [Read-only / Modifies agent config directories]

> Does this look correct? I will generate the commands once you confirm.
```

**For Sync**: Always propose a Dry Run first before offering to Apply.

### Phase 3: Command Execution

Wait for explicit confirmation (`yes`, `looks good`, `ok`).

---

## [Audit] Structural Compliance Check

### Step 1: Run Deterministic Scanner
```bash
python3 plugins/plugin-manager/skills/plugin-maintenance/scripts/audit_structure.py
```
> For deeper semantic + security checks, invoke `analyze-plugin` from `agent-plugin-analyzer`.

### Step 2: Manual Audit Checklist (if script unavailable)

For each plugin being audited, classify every file by type and check against Open Standards:

**File Type Classification:**
| Type | Path Pattern | Notes |
|------|-------------|-------|
| Skill definition | `skills/*/SKILL.md` | One per skill dir |
| Command | `commands/*.md` | Slash-command instructions |
| Reference | `skills/*/references/*.md` | Progressive disclosure content |
| Script | `scripts/*.py` | Python only — no .sh/.ps1 |
| Manifest | `.claude-plugin/plugin.json` | Required |
| Connectors | `CONNECTORS.md` | Required if Supercharged/Integration-Dependent |
| Diagram | `*.mmd` | Architecture diagrams |
| README | `README.md` | Required |

**7 Structural Dimensions:**

| Dimension | Pass Condition |
|-----------|---------------|
| **Layout** | Each skill has its own directory. No flat file mixing. |
| **Progressive Disclosure** | Every `SKILL.md` is under 500 lines. Deep content is in `references/`. |
| **Naming** | Plugin name: `kebab-case`, lowercase. Skill names: same convention, matching directory. |
| **README Quality** | Has directory tree, usage examples, skill table. |
| **CONNECTORS.md** | Present if plugin uses external tools. Uses `~~category` abstraction. |
| **Architecture fit** | Is Standalone / Supercharged / Integration-Dependent clearly declared? |
| **plugin.json** | Has unique `name`, `version`, `description`, `author.url`, `repository`. |

**SKILL.md Frontmatter Quality Checks:**
- [ ] `description` written in third person
- [ ] Includes specific trigger phrases ("Trigger when...")
- [ ] Under 1024 characters
- [ ] `name` matches directory name (kebab-case, lowercase)

**SKILL.md Body Structure Checks:**
- [ ] Clear numbered phases or execution steps
- [ ] Uses Recap-Before-Execute for destructive operations
- [ ] Tables used for structured comparisons
- [ ] Links to `references/` for deep content (not inline)
- [ ] `allowed-tools` declared if tool-restricted

**Three Compliance Absolutes (from Open Standards):**
1. All skills MUST end with a Source Transparency Declaration if querying external sources
2. If plugin generates `.html`, `.svg`, or `.js` artifacts, MUST implement Client-Side Compute Sandbox (hardcoded loop bounds) + XSS Compliance Gate (no external script tags)
3. Sub-agents MUST have an explicit `tools:` allowlist

### Step 3: Flag and Report
For each violation found, report with severity:
- **CRITICAL** — Missing `plugin.json`, `shell=True` in scripts, hardcoded credentials
- **HIGH** — SKILL.md over 500 lines, name convention violations, missing `allowed-tools`
- **MEDIUM** — Missing `CONNECTORS.md` for tool-using plugin, missing fallback-tree
- **LOW** — Missing README, no `repository` in plugin.json

> For L5 maturity scoring, invoke the `l5-red-team-auditor` agent from `agent-plugin-analyzer`.

---

## [Sync] Agent Environment Synchronization

#### Preview Changes (Always Run First)
```bash
python3 plugins/plugin-manager/skills/plugin-maintenance/scripts/sync_with_inventory.py --dry-run
```

#### Apply Changes
```bash
python3 plugins/plugin-manager/skills/plugin-maintenance/scripts/sync_with_inventory.py
```

### Post-Sync Verification
1. Check `local-plugins-inventory.json` (generated in project root) for current state.
2. Confirm custom plugins (not in vendor list) still present in `plugins/`.
3. Confirm artifacts for removed vendor plugins are gone from `.agent`, `.gemini`, etc.

---

## [README] Generate Missing Documentation
```bash
python3 plugins/plugin-manager/skills/plugin-maintenance/scripts/generate_readmes.py --apply
```

---

## Escalation Taxonomy

| Condition | Response |
|-----------|----------|
| "Vendor directory not found" | Clone vendor: `git clone https://github.com/richfrem/agent-plugins-skills.git .vendor/agent-plugins-skills` |
| `shell=True` detected in any script | STOP — CRITICAL: Command Injection Vector. Report before proceeding. |
| Custom plugin accidentally cleaned | STOP. Restore via `git checkout -- plugins/<name>/`. Never re-run until cause identified. |
| SKILL.md exceeds 500 lines | FLAG HIGH: Progressive Disclosure Violation. Suggest extracting to `references/`. |

---

## When to Use
- **After adding a new plugin** — run Audit to verify correct structure
- **After removing a vendor plugin** — run Sync to clean orphaned agent artifacts
- **Periodically** — to catch drift or accidental file placements
- **Before a release** — to ensure clean distribution state

## Next Actions
- Run `agent-bridge` from `plugin-mapper` to deploy updated plugins to agent environments.
- Run `l5-red-team-auditor` from `agent-plugin-analyzer` for full L5 maturity assessment.
- Run `create-skill` from `agent-scaffolders` to fix scaffolding gaps in audited plugins.
