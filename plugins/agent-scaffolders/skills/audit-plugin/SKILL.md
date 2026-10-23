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

- **No raw filesystem symlinks**: Under APM, skills must be self-contained packages. Raw symlinks are prohibited.
- **Hub-first copy-manifest**: Shared scripts and references live in the plugin root hub and are mapped to skills in `symlinks.json` (strategy: "copy").
- **Portability**: No hardcoded paths (`/Users/`, `/home/`); use relative paths or `${CLAUDE_PLUGIN_ROOT}`.
- **Manifest schemas**: `apm.yml` defines APM package metadata; `.claude-plugin/plugin.json` author field must be an object `{"name": "...", "email": "..."}`.

## Quick start

Run structural and component audits for target plugin:

```bash
# 1. Structure audit: check manifests, copy-manifest sync & absence of raw symlinks
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>

# 2. Copy-manifest drift check: ensure spoke copies match canonical sources
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py --check

# 3. Skills audit: scan all skills within plugin against authoring standards
python3 scripts/audit_skill.py plugins/<plugin-name> --all --mode source --json

# 4. Sub-agents audit: check all agents in plugin for frontmatter and prompt structure
python3 scripts/audit_sub_agent.py plugins/<plugin-name> --all --json

# 5. Rules audit: check any rules defined in plugin for invariants and line budgets
python3 scripts/audit_rule.py plugins/<plugin-name> --all --json
```

## Workflow

1. **Structure & Manifest**: Run `audit_plugin_structure.py` to ensure `apm.yml` and `.claude-plugin/plugin.json` conformance, and verify that shared spoke resources match the copy-manifest without raw symlinks.
2. **Skills Audit**: Run `audit_skill.py` across all skills in the plugin to verify progressive disclosure line budgets, frontmatter, and `evals/evals.json` boolean contracts.
3. **Sub-Agents Audit**: Run `audit_sub_agent.py` on `plugins/<plugin>/agents/` to verify second-person system prompts, model/color properties, and trigger `<example>` blocks.
4. **Rules & Invariants Audit**: Run `audit_rule.py` on `plugins/<plugin>/rules/` to ensure invariant structure, zero calendar dates, zero absolute paths, and line budget compliance.
5. **Copy-Manifest Hygiene & Zero Drift**: Verify with `materialize_copies.py --check` that all skill spoke copies match their canonical sources. Verify zero hardcoded tokens or machine-specific paths.

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
