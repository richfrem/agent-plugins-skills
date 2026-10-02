---
name: create-hook
plugin: agent-scaffolders
description: >
  Scaffolds a new event-driven hook in a plugin. NOT for creating skills (use `create-skill`) and NOT for GitHub Actions agentic workflows (use `create-agentic-workflow`).
argument-hint: "[event-type or use case]"
allowed-tools: Bash, Read, Write
---

# Create Hook (create-hook)

Scaffolds event-driven lifecycle hooks (e.g. `PreToolUse`, `PostToolUse`, `Stop`, `PermissionRequest`) in plugin configuration or skill frontmatter.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Event Scope**: Only for lifecycle hooks. For standalone skills, use `create-skill`. For CI/CD or agentic workflows, use `create-github-action` or `create-agentic-workflow`.
- **Cross-Platform Commands**: Hook commands must support macOS/Linux and Windows via `python3 ... || python ...` syntax with `${CLAUDE_PLUGIN_ROOT}` path anchors.
- **Project Context Guards**: Hook scripts must verify repository context on entry (e.g. check `.agent/` or `context/`) and exit silently (return code 0) if uninitialized.
- **Minimal Latency**: Keep synchronous hook handlers lean to prevent blocking the agent execution loop.

## Quick start

```bash
python3 plugins/agent-scaffolders/scripts/scaffold.py \
  --type hook \
  --name check-command \
  --path plugins/<plugin>/hooks \
  --event PreToolUse \
  --action command
```

## Workflow

1. **Phase 1: Event & Scope Selection**: Determine lifecycle trigger event (`PreToolUse`, `PostToolUse`, `Stop`), placement scope (global `hooks.json` vs skill frontmatter), and action type (`command`, `prompt`, `agent`).
2. **Phase 2: Hook Configuration**: Draft configuration entry with event identifier, target tool matcher pattern, and action parameters.
3. **Phase 3: Script Implementation**: For command hooks, author script with cross-platform fallback, silent project guards, and deterministic exit codes.
4. **Phase 4: Linting & Testing**: Execute `hook_linter.py` on created handler scripts and verify schema validity.

## Verification

```bash
# Lint the hook handler script
python3 plugins/agent-scaffolders/scripts/hook_linter.py plugins/<plugin>/hooks/<script>.py

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/agent-scaffolders/skills/create-hook --mode source
```

## References
- [fallback-tree.md](references/fallback-tree.md) - Fallback tree for scaffolding failures.
- [references/patterns.md](references/patterns.md) - Common event-driven hook patterns.
- [references/advanced.md](references/advanced.md) - Advanced handler types and lifecycle nuances.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Hook validation and acceptance criteria.
