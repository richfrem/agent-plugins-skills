---
name: audit-plugin
plugin: agent-scaffolders
description: >
  Use when the user asks to audit or validate a plugin, check its structure or
  .claude-plugin/plugin.json, review components, or confirm compliance. Also trigger
  after plugin components change. Audit the whole plugin here; use audit-skill for one skill.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Audit Plugin (`audit-plugin`)

Performs comprehensive validation of a plugin against structure standards, naming conventions, and component requirements.

## Contents

- [Dependencies](#dependencies)
- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Dependencies

Requires Python 3.8+ and standard library modules.

## Constraints

- **File-level symlinks only**: Directory symlinks violate plugin architecture policy.
- **Hub-first asset layout**: Reusable scripts and references live in plugin root hub, symlinked into skills.
- **Portability**: No hardcoded paths (`/Users/`, `/home/`); use relative paths or `${CLAUDE_PLUGIN_ROOT}`.
- **Manifest schema**: `.claude-plugin/plugin.json` author field must be an object `{"name": "...", "email": "..."}`.

## Quick start

```bash
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
```

## Workflow

1. **Structure & Manifest**: Verify `.claude-plugin/plugin.json` exists with object author schema.
2. **Component Linting**: Validate agents, hooks (`validate_hook_schema.py`), and skills.
3. **Symlink Hygiene**: Verify spoke symlinks resolve cleanly to plugin root hubs.
4. **Contract Compliance**: Confirm `evals/evals.json` routing arrays use `should_trigger` boolean schema.
5. **Security Scan**: Verify zero hardcoded tokens, secrets, or machine-specific absolute paths.

## Verification

```bash
# Validate plugin structure compliance
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
# Audit marketplace source paths (if marketplace.json present)
python3 scripts/audit_marketplace_sources.py .
```

## References

- [audit-plugin-guide.md](references/audit-plugin-guide.md) — Comprehensive audit rules and error codes.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Plugin validation acceptance criteria.
- [fallback-tree.md](references/fallback-tree.md) — Escalation protocol for structural audit failures.
