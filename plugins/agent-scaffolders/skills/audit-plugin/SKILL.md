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

Run structural and component audits for target plugin:

```bash
# 1. Structure audit: check hub-and-spoke symlinks & manifest
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>

# 2. Skills audit: scan all skills within plugin against authoring standards
python3 scripts/audit_skill.py plugins/<plugin-name> --all --mode source --json

# 3. Sub-agents audit: check all agents in plugin for frontmatter and prompt structure
python3 scripts/audit_sub_agent.py plugins/<plugin-name> --all --json

# 4. Rules audit: check any rules defined in plugin for invariants and line budgets
python3 scripts/audit_rule.py plugins/<plugin-name> --all --json
```

## Workflow

1. **Structure & Manifest**: Verify `.claude-plugin/plugin.json` exists with object author schema. Run `audit_plugin_structure.py` to ensure spoke resources are file-level symlinks to plugin root hubs.
2. **Skills Audit**: Run `audit_skill.py` across all skills in the plugin to verify progressive disclosure line budgets, frontmatter, and `evals/evals.json` boolean contracts.
3. **Sub-Agents Audit**: Run `audit_sub_agent.py` on `plugins/<plugin>/agents/` to verify second-person system prompts, model/color properties, and trigger `<example>` blocks.
4. **Rules & Invariants Audit**: Run `audit_rule.py` on `plugins/<plugin>/rules/` to ensure invariant structure, zero calendar dates, zero absolute paths, and line budget compliance.
5. **Symlink Hygiene & Security**: Verify all symlinks are registered in `symlinks.json` via `symlink_manager.py audit`. Verify zero hardcoded tokens or machine-specific paths.

## Verification

```bash
# Full verification pipeline for a plugin
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
python3 scripts/audit_skill.py plugins/<plugin-name> --all --mode source
python3 scripts/audit_sub_agent.py plugins/<plugin-name> --all
python3 scripts/audit_rule.py plugins/<plugin-name> --all
```

## References

- [audit-plugin-guide.md](references/audit-plugin-guide.md) — Comprehensive audit rules and error codes.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Plugin validation acceptance criteria.
- [fallback-tree.md](references/fallback-tree.md) — Escalation protocol for structural audit failures.
