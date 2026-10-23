> Retired skill `create-hook`, kept as the **create-hook** mode of `authoring-instructions`. Body unchanged apart from link targets and corrected commands. Frontmatter removed.
>
> Original description: Scaffolds a new event-driven hook in a plugin. NOT for creating skills (use `authoring-skills`) and NOT for GitHub Actions agentic workflows (use `authoring-github-workflows`).

# Create Hook (create-hook)

Scaffolds event-driven lifecycle hooks (e.g. `PreToolUse`, `PostToolUse`, `Stop`, `PermissionRequest`) in plugin configuration or skill frontmatter.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Event Scope**: Only for lifecycle hooks. For standalone skills, use `authoring-skills`. For CI/CD or agentic workflows, use `authoring-github-workflows` or `authoring-github-workflows`.
- **Cross-Platform Commands**: Hook commands must support macOS/Linux and Windows via `python3 ... || python ...` syntax with `${CLAUDE_PLUGIN_ROOT}` path anchors.
- **Project Context Guards**: Hook scripts must verify repository context on entry (e.g. check `.agent/` or `context/`) and exit silently (return code 0) if uninitialized.
- **Minimal Latency**: Keep synchronous hook handlers lean to prevent blocking the agent execution loop.

## Quick start

```bash
python3 scripts/scaffold_hook.py --event PreToolUse --name check-command --plugin-root plugins/<plugin>
```

## Workflow

1. **Phase 1: Event & Scope Selection**: Determine lifecycle trigger event (`PreToolUse`, `PostToolUse`, `Stop`), placement scope (global `hooks.json` vs skill frontmatter), and action type (`command`, `prompt`, `agent`).
2. **Phase 2: Hook Configuration**: Draft configuration entry with event identifier, target tool matcher pattern, and action parameters.
3. **Phase 3: Script Implementation**: For command hooks, author script with cross-platform fallback, silent project guards, and deterministic exit codes.
4. **Phase 4: Linting & Testing**: Execute `hook_linter.py` on created handler scripts and verify schema validity.

## Verification

```bash
# Lint the hook handler script
python3 scripts/hook_linter.py plugins/<plugin>/hooks/<script>.py
python3 scripts/validate_hook_schema.py plugins/<plugin>/hooks/hooks.json

# Audit skill compliance
python3 plugins/agent-extension-authoring/skills/authoring-skills/scripts/audit_skill.py plugins/agent-extension-authoring/skills/authoring-instructions --mode source
```

## References
- [fallback-tree.md](../fallback-tree.md) - Fallback tree for scaffolding failures.
- [hook-patterns.md](../hook-patterns.md) - Common event-driven hook patterns.
- [hook-advanced.md](../hook-advanced.md) - Advanced handler types and lifecycle nuances.
- [acceptance-criteria.md](../acceptance-criteria.md) - Hook validation and acceptance criteria.
