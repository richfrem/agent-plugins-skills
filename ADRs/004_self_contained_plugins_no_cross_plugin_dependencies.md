# ADR-004: Self-Contained Plugins - No Cross-Plugin Script Dependencies

## Status
Accepted

## Context

Several plugins in this repo declared dependencies on scripts from other plugins
using paths like `${CLAUDE_PLUGIN_ROOT}/../other-plugin/scripts/validate.sh` and
documented these via a local `CONNECTORS.md` convention. For example, `audit-plugin`
invoked `validate-agent.sh` and `validate-hook-schema.sh` from `agent-scaffolders`.

Anthropic's official plugin documentation (https://code.claude.com/docs/en/plugins)
defines no cross-plugin dependency mechanism. There is no `dependencies` field in
`plugin.json` that Claude Code resolves at install time. A user who installs one
plugin has no guarantee the other plugin is present.

Two failure modes were confirmed:

**Failure 1: Silent breakage at runtime.**
`${CLAUDE_PLUGIN_ROOT}/../other-plugin/scripts/script.sh` resolves correctly only when
both plugins happen to be installed in the same parent directory. This is fragile and
breaks in any non-standard installation layout.

**Failure 2: CONNECTORS.md was misused.**
The `CONNECTORS.md` convention in this repo was designed for MCP tool category
abstractions (`~~filesystem -> Read/Write`, `~~crm -> Salesforce`). It was being
repurposed to document cross-plugin script dependencies, which is a different concern
and has no runtime enforcement.

## Decision

**Plugins and skills must be self-contained.**

1. **No cross-plugin script paths.** Any script a plugin needs must live in that
   plugin's own `scripts/` directory. If the same script is needed by multiple plugins,
   each plugin gets its own copy.

2. **Copy, don't symlink across plugins.** When a script originates in another plugin,
   copy it into the target plugin's `scripts/` folder. Update all path references to
   use `${CLAUDE_PLUGIN_ROOT}/scripts/<script>`.

3. **Skills access plugin scripts via file-level symlinks** per ADR-003. The canonical
   script lives at `plugin-name/scripts/script.py`. Skills that need it get a file-level
   symlink at `skills/skill-name/scripts/script.py -> ../../../scripts/script.py`.

4. **CONNECTORS.md is for MCP tool categories only.** Use `CONNECTORS.md` exclusively
   to map `~~category` abstractions to concrete MCP tool implementations. Do not use it
   to declare plugin-to-plugin dependencies.

5. **Empty CONNECTORS.md template files must be deleted.** A CONNECTORS.md that contains
   only the scaffold header ("Map abstract `~~category` tool requirements...") with no
   actual entries provides no value and creates noise.

## Migration Steps for Existing Cross-Plugin References

For each CONNECTORS.md that declares a cross-plugin script dependency:

```
1. Identify the scripts referenced from the other plugin
2. Copy those scripts into plugins/<this-plugin>/scripts/
3. Update all path references in SKILL.md / command files:
      FROM: ${CLAUDE_PLUGIN_ROOT}/../other-plugin/scripts/script.sh
      TO:   ${CLAUDE_PLUGIN_ROOT}/scripts/script.sh
4. For each skill that needs the script, create a file-level symlink:
      ln -s ../../../scripts/script.sh skills/skill-name/scripts/script.sh
5. Delete the CONNECTORS.md (or keep only if it has real ~~category entries)
```

## Consequences

- Plugins are fully portable and installable independently
- No silent runtime failures due to missing sibling plugins
- Scripts may be duplicated across plugins - this is intentional and acceptable
- `CONNECTORS.md` files are now rare and only appear when a plugin integrates
  external MCP tools requiring category abstraction

## Applied Fixes (as of 2026-03-22)

- `agent-plugin-analyzer/audit-plugin`: Copied `validate-agent.sh`,
  `validate-hook-schema.sh`, `test-hook.sh`, `hook-linter.sh` from `agent-scaffolders`
  into `agent-plugin-analyzer/scripts/`. Removed CONNECTORS.md.
- Deleted empty template CONNECTORS.md files from `exploration-cycle-plugin`,
  `agent-scaffolders/skills/continuous-skill-optimizer`,
  `agent-scaffolders/skills/manage-marketplace`, `rsvp-speed-reader`.
