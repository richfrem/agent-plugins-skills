---
concept: adr-004-self-contained-plugins---no-cross-plugin-script-dependencies
source: plugin-code
source_file: /Users/richardfremmerlid/Projects/agent-plugins-skills/ADRs/004_self_contained_plugins_no_cross_plugin_dependencies.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.624341+00:00
cluster: plugin-code
content_hash: be963a9c0cd817de
---

# ADR-004: Self-Contained Plugins - No Cross-Plugin Script Dependencies

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

1. **No cross-plugin script paths in deployed skills.** Any script a skill executes
   must be present in that plugin's own `scripts/` directory at install time.

2. **Source repo DRY via cross-plugin file-level symlinks.** In the mono-repo source,
   prefer a file-level symlink pointing to the canonical script rather than duplicating
   it. The bridge installer and `npx skills add` resolve these symlinks to physical
   copies when installing into `.agents/` -- so the installed skill is self-contained
   even if the source uses a symlink. See ADR-003 for the validated symlink resolution
   rules (file-level only; directory-level symlinks are dropped by npx).

3. **When duplication is unavoidable** (e.g. a plugin that will be distributed
   independently via npx without relying on the full mono-repo), copy the canonical
   script into the target plugin's `scripts/` folder and update all path references
   to use `${CLAUDE_PLUGIN_ROOT}/scripts/<script>`.

4. **Skills access plugin scripts via file-level symlinks** per ADR-003. The canonical
   script lives at `plugin-name/scripts/script.py`. Skills that need it get a file-level
   symlink at `skills/skill-name/scripts/script.py -> ../../../scripts/script.py`.

5. **CONNECTORS.md is for MCP tool categories only.** Use `CONNECTORS.md` exclusively
   to map `~~category` abstractions to concrete MCP tool implementations. Do not use it
   to declare plugin-to-plugin dependencies.

6. **Empty CONNECTORS.md template files must be deleted.** A CONNECTORS.md that contains
   only the scaffold header with no actual entries provides no value and creates noise.

## Migration Steps for Existing Cross-Plugin References

For each CONNECTORS.md that declares a cross-plugin script dependency:

```
1. Identify the scripts referenced from the other plugin
2. Copy those scripts into plugins/<this-plugin>/scripts/
3. Update all path references in SKILL.md / command files:
      FROM: ${CLAUDE_PLUGIN_ROOT}/../other-plugin/scripts/script.sh
      TO:   ${CLAUDE_PLUGIN_ROOT}/scripts/script.py
4. For each skill that needs the script, create a file-level symlink:
      ln -s ../../../scripts/script.py skills/skill-name/scripts/script.py
5. Delete the CONNECTORS.md (or keep only if it has real ~~category entries)
```

## Consequences

- Plugins are fully portable and installable independently at deploy time
- No silent runtime failures due to missing sibling plugins
- In the mono-repo source, DRY is maintained via cross-plugin file-level symlinks;
  physical copies only exist in `.agents/` after the installer res

*(content truncated)*

## See Also

- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-manager-plugin]]
- [[adr-002-multi-skill-script-centralization]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `/Users/richardfremmerlid/Projects/agent-plugins-skills/ADRs/004_self_contained_plugins_no_cross_plugin_dependencies.md`
- **Indexed:** 2026-04-17T06:42:09.624341+00:00
