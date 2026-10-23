> Retired skill `create-plugin`, kept as the **create-plugin** mode of `authoring-plugins`. Body unchanged apart from link targets and the parts rewritten for the self-contained end state (no copy manifest, optional `apm.yml`, delegation to sibling skills by name). Frontmatter removed.
>
> Original description: Scaffolds a new top-level agent plugin directory. NOT for scaffolding single skills (use `authoring-skills`) and NOT for adding MCP integrations to existing plugins (use `authoring-skills`).

# Create Plugin (`create-plugin`)

Scaffolds a complete agent plugin with multi-platform manifests and standard directory layout.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **APM manifest is optional**: APM installs a plugin as it is; an `apm.yml` inside the plugin is not required (it is local and untracked in this repository). Packaging is the `packaging-with-apm` skill.
- **Clean metadata**: `.claude-plugin/plugin.json` must never declare `skills`, `agents`, or `hooks` arrays (auto-discovered).
- **Author object**: `author` must be an object `{"name": "...", "email": "..."}`, never a string.
- **Self-contained skills**: scripts, references and assets live inside the skill that uses them; the plugin root holds no shared scripts, no copy manifest and no symlinks.
- **No raw filesystem symlinks**: Under APM, skills must be self-contained packages. Raw symlinks are prohibited.
- **No cross-plugin imports**: Never import Python code from another plugin.

## Quick start

```bash
python3 scripts/scaffold_plugin.py --name <plugin-name> --path plugins [--with-hooks] [--with-mcp]
```

## Workflow

1. **Scaffold Root**: Run `scaffold_plugin.py` to create `.claude-plugin/plugin.json`, `skills/` and `README.md`.
2. **Check the manifest**: `.claude-plugin/plugin.json` is minimal, with an author object and no `skills`, `agents` or `hooks` arrays.
3. **Scaffold Components**: Use the `authoring-skills` skill for skills, `authoring-instructions` for rules and hooks, and `authoring-subagents` for sub-agents.
4. **Audit**: Run the audit mode of this skill to verify structure and schemas.

## Verification

```bash
# Validate plugin structure compliance
python3 plugins/agent-extension-authoring/scripts/audit_plugin_structure.py plugins/<plugin-name>
# If hooks are present, use the hooks mode of the authoring-instructions skill to validate hooks.json
```

## References

- [create-plugin-guide.md](../create-plugin-guide.md) — Detailed workflows and manifest templates.
- [acceptance-criteria.md](../acceptance-criteria.md) — Plugin creation acceptance criteria.
- [fallback-tree.md](../fallback-tree.md) — Troubleshooting and error recovery tree.
