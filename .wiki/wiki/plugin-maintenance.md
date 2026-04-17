---
concept: plugin-maintenance
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/maintain-plugins/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.109748+00:00
cluster: skill
content_hash: 27b45652e5f50f57
---

# Plugin Maintenance

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: maintain-plugins
description: >
  Audits, synchronizes, and maintains the health of the plugin ecosystem.
  Handles structural compliance checks against Open Standards, agent environment
  sync (install + cleanup orphans), and README scaffolding. Trigger when
  validating new plugins, syncing plugins to agent configs, or performing
  routine ecosystem health checks.
allowed-tools: Bash, Write, Read
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Plugin Maintenance

## Overview
This skill is the ecosystem health hub. It covers three operations:
- **Audit** — structural compliance checking against Open Standards
- **Sync** — keep agent environments in sync with `plugins/`, cleaning up orphaned artifacts
- **README** — scaffold missing documentation

**Core constraint**: Custom, project-specific plugins are NEVER deleted during sync. Only vendor-managed plugins that have been locally removed are cleaned up.

## References
- Sync process guide: `cleanup_process.md`
- Sync flow diagram: `cleanup_flow.mmd`

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
python3 ./scripts/audit_structure.py
```
> For deeper semantic + security checks, invoke `analyze-plugin` from `agent-plugin-analyzer`.

### Step 1.5: Path Portability Audit
Run after every structure scan to catch hardcoded or non-portable paths (ADR-003/004):
```bash
python3 plugins/agent-plugin-analyzer/scripts/audit_plugin_paths.py plugins/
```
**Expected output**: `✅ Clean! 0 violations found.`

If violations are found, invoke the `fix-plugin-paths` skill from `agent-plugin-analyzer` to
remediate each file. A clean path audit is a mandatory gate before any merge or release.

**Common violations it catches:**
- Self-referential absolute paths (`plugins/<name>/scripts/foo.py` → `./scripts/foo.py`)
- Environment-specific `.agents/skills/<skill>/scripts/` paths that break on reinstall
- Absolute machine paths (`/Users/<name>/...`) that break portability across machines

### Step 2: Manual Audit Checklist (if script unavailable)

For each plugin being audited, classify every file by type and check against Open Standards:

**File Type Classification:**
| Type | Path Pattern | Notes |
|------|-------------|-------|
| Skill definition | `skills/*/SKILL.md` | One per skill dir |
| Command | `commands/*.md` | Slash-command instructions |
| Reference | `skills/*/references/*.md` | Progressive disclosure content |
| Script | `scripts/*.py` | Python only — no .sh/.ps1 |
| Manifest | `../../../.claude-plugin/plugin.json` | Required |
| Connectors | `CONNECTORS.md` | Required if Supercharged/Integration-Dependent |
| Diagram | `*.mmd` | A

*(content truncated)*

## See Also

- [[acceptance-criteria-plugin-maintenance]]
- [[procedural-fallback-tree-plugin-maintenance]]
- [[acceptance-criteria-plugin-maintenance]]
- [[procedural-fallback-tree-plugin-maintenance]]
- [[acceptance-criteria-plugin-maintenance]]
- [[procedural-fallback-tree-plugin-maintenance]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/maintain-plugins/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.109748+00:00
