---
name: authoring-plugins
plugin: agent-extension-authoring
description: >-
  Scaffolds and audits whole agent plugins. Use when the user wants to create a new plugin directory (manifest, README, skills folder) or to audit or validate an existing plugin: its structure, .claude-plugin/plugin.json, components, portability and compliance. Also use after a plugin's components change. Not for a single skill (use authoring-skills), a single sub-agent (use authoring-subagents), rules, AGENTS.md or hooks (use authoring-instructions), or APM packaging (use packaging-with-apm).
argument-hint: "[create|audit] [plugin-name or path]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Authoring Plugins (`authoring-plugins`)

Creates a plugin skeleton and audits a plugin as a whole; component audits are delegated to the sibling skills by name.

## Contents

- [Constraints](#constraints) • [Modes](#modes) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Self-contained skills**: scripts, references and assets live inside the skill that uses them; no plugin-root shared files, no symlinks.
2. **Clean manifest**: `.claude-plugin/plugin.json` has an author object and never lists `skills`, `agents` or `hooks` (they are auto-discovered).
3. **`apm.yml` is optional**: APM installs a plugin as it is; packaging belongs to `packaging-with-apm`.
4. **Portable**: no `/Users/` or `/home/` paths; use relative paths or `${CLAUDE_PLUGIN_ROOT}`.
5. **No cross-plugin imports**; refer to other plugins' skills by name.
6. Audits are read-only.

## Modes

| Mode | Use when | Entry point | Reference |
|---|---|---|---|
| `create` | New plugin | `scripts/scaffold_plugin.py` | [create-plugin.md](references/modes/create-plugin.md) |
| `audit` | Validate a plugin | `scripts/audit_plugin_structure.py`, `scripts/audit.py` | [audit-plugin.md](references/modes/audit-plugin.md) |

## Quick start

```bash
python3 scripts/scaffold_plugin.py --name <plugin-name> --path plugins [--with-hooks] [--with-mcp]
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
python3 scripts/audit.py --path plugins/<plugin-name>
```

`audit.py` runs the per-skill audit through the sibling `authoring-skills` skill and warns when it is not installed.

## Workflow

1. Pick the mode and read its reference.
2. Create: scaffold, then add components with `authoring-skills`, `authoring-subagents` and `authoring-instructions`.
3. Audit: run both scripts, then delegate skills, sub-agents, rules and hooks to those skills by name.
4. On failure follow [fallback-tree.md](references/fallback-tree.md).

## Verification

```bash
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
python3 scripts/audit.py --path plugins/<plugin-name>
```

Tests: `python3 -m pytest tests`. Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [create-plugin.md](references/modes/create-plugin.md) • [audit-plugin.md](references/modes/audit-plugin.md)
- Detail: [create-plugin-guide.md](references/create-plugin-guide.md) • [audit-plugin-guide.md](references/audit-plugin-guide.md)
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
- Templates: [README.md.jinja](assets/templates/README.md.jinja)
