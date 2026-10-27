> Retired skill `create-hook`, kept as the **create-hook** mode of `authoring-instructions`.

# Create Hook (create-hook)

Scaffolds event-driven lifecycle hooks (e.g. `PreToolUse`, `PostToolUse`, `Stop`, `PermissionRequest`, `SessionStart`) in `plugins/<plugin>/.apm/hooks/hooks.json` and writes a harness-neutral Python handler stub.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Event Scope**: Only for lifecycle hooks. For standalone skills, use `authoring-skills`. For CI/CD or agentic workflows, use `authoring-github-workflows`.
- **APM-Native Hook Location**: Hooks reside in `plugins/<plugin>/.apm/hooks/hooks.json` with scripts alongside them in `plugins/<plugin>/.apm/hooks/<name>.py`.
- **Cross-Platform Commands**: Hook commands must support macOS/Linux and Windows via `python3 "${CLAUDE_PLUGIN_ROOT}/.apm/hooks/<name>.py" || python "${CLAUDE_PLUGIN_ROOT}/.apm/hooks/<name>.py"`.
- **Harness-Neutral Scripts (**SF-11**)**: Hook scripts run under every target harness (`claude`, `copilot`, `codex`; note that Antigravity supports hooks at project scope via `.gemini/settings.json`). Scripts must use `Path(__file__).resolve()` to locate sibling files and `context/` for project state—never hardcode `.claude/` or `.agents/`.
- **Project Context Guards**: Hook scripts must verify repository context on entry (e.g. check `context/`) and exit silently (return code 0) if uninitialized.
- **Minimal Latency**: Keep synchronous hook handlers lean to prevent blocking the agent execution loop.

## Quick start

```bash
python3 scripts/scaffold_hook.py --event PreToolUse --name check-command --plugin-root plugins/<plugin>
```

## Workflow

1. **Phase 1: Event & Scope Selection**: Determine lifecycle trigger event (`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`), placement scope (`.apm/hooks/hooks.json` vs skill frontmatter), and action type (`command`, `prompt`, `agent`).
2. **Phase 2: Hook Configuration**: Run `scripts/scaffold_hook.py` to merge the event entry into `<plugin-root>/.apm/hooks/hooks.json`.
3. **Phase 3: Script Implementation**: For command hooks, implement `<plugin-root>/.apm/hooks/<name>.py` with cross-platform fallback, silent project guards (`context/`), `Path(__file__).resolve()`, and deterministic exit codes.
4. **Phase 4: Linting & Testing**: Execute `hook_linter.py` on created handler scripts and verify schema validity with `validate_hook_schema.py`.

## Verification

```bash
# Lint the hook handler script and validate hooks.json schema
python3 scripts/hook_linter.py plugins/<plugin>/.apm/hooks/<script>.py
python3 scripts/validate_hook_schema.py plugins/<plugin>/.apm/hooks/hooks.json

# Audit skill compliance
python3 ../authoring-skills/scripts/audit_skill.py . --mode source
```

## References
- [fallback-tree.md](../fallback-tree.md) - Fallback tree for scaffolding failures.
- [hook-patterns.md](../hook-patterns.md) - Common event-driven hook patterns.
- [hook-advanced.md](../hook-advanced.md) - Advanced handler types and lifecycle nuances.
- [acceptance-criteria.md](../acceptance-criteria.md) - Hook validation and acceptance criteria.
