# Create Plugin (`create-plugin`)

Scaffolds a complete APM-native agent plugin with `apm.yml`, `.claude-plugin/plugin.json`, `.apm/skills/`, and `README.md`.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **APM Package Layout**: Primitives are authored exclusively under `.apm/` (`.apm/skills/`, `.apm/agents/`, `.apm/hooks/`, `.apm/prompts/`, `.apm/instructions/`). Duplicate primitive folders outside `.apm/` are forbidden.
- **Dual manifests**: `apm.yml` at the plugin root defines APM package metadata; `.claude-plugin/plugin.json` must never declare `skills`, `agents`, `hooks`, or `commands` arrays (auto-discovered).
- **Author object**: `author` in `.claude-plugin/plugin.json` must be an object `{"name": "...", "email": "..."}`, never a string.
- **Self-contained skills**: scripts, references and assets live inside `.apm/skills/<skill>/`; the plugin root holds no shared scripts, no copy manifest and no symlinks.
- **No raw filesystem symlinks**: Under APM, skills must be self-contained packages. Raw symlinks are prohibited.
- **No cross-plugin imports**: Never import Python code from another plugin.

## Quick start

```bash
python3 scripts/scaffold_plugin.py --name <plugin-name> --path plugins [--with-hooks] [--with-mcp]
```

## Workflow

1. **Scaffold Root**: Run `scaffold_plugin.py` to create `apm.yml`, `.claude-plugin/plugin.json`, `.apm/skills/` and `README.md`.
2. **Check the manifests**: Verify `apm.yml` and `.claude-plugin/plugin.json` (minimal metadata, author object, no `skills`, `agents` or `hooks` arrays).
3. **Scaffold Components**: Use the `authoring-skills` skill for skills (`.apm/skills/`), `authoring-instructions` for rules and hooks (`.apm/hooks/`), and `authoring-subagents` for sub-agents (`.apm/agents/`).
4. **Audit**: Run the audit mode of this skill to verify structure and schemas.

## Verification

```bash
# Validate plugin structure compliance
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
python3 scripts/audit.py --path plugins/<plugin-name>
# If hooks are present, use the hooks mode of the authoring-instructions skill to validate .apm/hooks/hooks.json
```

## References

- [create-plugin-guide.md](../create-plugin-guide.md) — Detailed workflows and manifest templates.
- [acceptance-criteria.md](../acceptance-criteria.md) — Plugin creation acceptance criteria.
- [fallback-tree.md](../fallback-tree.md) — Troubleshooting and error recovery tree.
