---
name: create-plugin
plugin: agent-scaffolders
description: >
  Scaffolds a new top-level agent plugin directory. NOT for scaffolding single skills (use `create-skill`) and NOT for adding MCP integrations to existing plugins (use `create-mcp-integration`).
argument-hint: "[plugin-name]"
allowed-tools: Bash, Read, Write
---

# Create Plugin (`create-plugin`)

Scaffolds a complete agent plugin with multi-platform manifests and standard directory layout.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **APM Package Manifest**: Every plugin must include an `apm.yml` specifying package name (`@richfrem/<plugin>`), version, description, and client targets (`claude,copilot,codex,antigravity`).
- **Clean metadata**: `.claude-plugin/plugin.json` must never declare `skills`, `agents`, or `hooks` arrays (auto-discovered).
- **Author object**: `author` must be an object `{"name": "...", "email": "..."}`, never a string.
- **Hub-first copy-manifest**: Reusable scripts live in `plugins/<plugin>/scripts/` and are mapped to skills in `symlinks.json` (strategy: "copy").
- **No raw filesystem symlinks**: Under APM, skills must be self-contained packages. Raw symlinks are prohibited.
- **No cross-plugin imports**: Never import Python code from another plugin.

## Quick start

```bash
# Scaffold plugin root directory structure
mkdir -p plugins/<plugin-name>/{.claude-plugin,skills,references,scripts,tests}
```

## Workflow

1. **Scaffold Root**: Create directory structure with `apm.yml`, `.claude-plugin/plugin.json`, and `README.md`.
2. **Configure Multi-Platform Manifests**:
   - `apm.yml`: Primary package manifest declaring targets `claude,copilot,codex,antigravity`.
   - `.claude-plugin/plugin.json`: Minimal Claude compatibility manifest with author object.
3. **Scaffold Components**: Use `create-skill` for skills and `create-hook` for hooks.
4. **Copy-Manifest Provisioning**: Register shared hub scripts/references in `symlinks.json` and run `materialize_copies.py`.
5. **Audit**: Run `audit-plugin` to verify structure, schemas, and copy-manifest alignment.

## Verification

```bash
# Validate plugin structure compliance
python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
# Validate copy-manifest drift
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py --check
# Validate hook schemas if hooks present
python3 scripts/validate_hook_schema.py plugins/<plugin-name>/hooks/hooks.json
```

## References

- [create-plugin-guide.md](references/create-plugin-guide.md) — Detailed workflows and manifest templates.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Plugin creation acceptance criteria.
- [fallback-tree.md](references/fallback-tree.md) — Troubleshooting and error recovery tree.
