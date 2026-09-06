# ADR-003: Plugin Skill Resource Sharing via Mirrored Folder Structure and File-Level Symlinks

## Status
Accepted - Validated

Validated across 15+ plugins. All installed correctly via `npx skills add` with all symlinks
resolved to real files. Approach confirmed working and aligned with the open Agent Skills spec
(https://agentskills.io/specification).

## Context

Plugins in this repo can contain both a `skills/` directory (installed by `npx skills add`) and a
`commands/` directory (installed by the bridge plugin). Both may reference shared resources: scripts,
assets/templates, and reference documents.

The naive approach is to put these resources inside the skill directory and use folder-level symlinks or
duplicate copies. Three failure modes were discovered and validated through direct testing:

**Failure 1: Folder-level symlinks are silently dropped by npx.**
`npx skills add` resolves file-level symlinks (copying the real content) but silently drops entire
directory-level symlinks. A skill that symlinks `scripts -> ../../scripts` will install with an empty
`scripts/` directory or no `scripts/` directory at all.

**Failure 2: Resources buried inside the skill are inaccessible to the command.**
When a plugin has both a `commands/` file and a `skills/` directory, the command's script references
point to paths that only exist inside the skill subtree. These paths are not installed anywhere accessible
when only the command is installed via bridge plugin.

**Failure 3: Absolute hardcoded paths break portability.**
SKILL.md files that invoke scripts as `python ./adr_manager.py` fail when the agent runs from the
project root. And paths hardcoded to `.agents/skills/<name>/scripts/...` break when the install
location changes. The open Agent Skills spec (agentskills.io) specifies that file references in
SKILL.md should use **relative paths from the skill root** (e.g. `scripts/extract.py`), which the
installed skill resolves correctly regardless of install location.

## Decision

**Core principle: Zero duplication. One file, one location.**

Every script, asset, and reference document must exist in exactly one place in the plugin source tree.
Duplication causes drift — two copies diverge silently and there is no way to know which is authoritative.
The plugin root is always the authoritative location.

**Rule 1: Scripts, assets, and references live at plugin root.**

All resources belong at the plugin root regardless of how many skills use them:

```
plugins/<plugin-name>/
  scripts/           <- real files, canonical source (no copies elsewhere)
  assets/            <- real files, canonical source (no copies elsewhere)
    templates/
    resources/
  references/        <- real files, canonical source (no copies elsewhere)
  agents/            <- agent instruction files
  commands/          <- command instruction files
  hooks/             <- hook configuration
  skills/
    <skill-name>/
      SKILL.md
      scripts/       <- real directory, contains ONLY symlinks -> plugin root
      assets/        <- real directory, contains ONLY symlinks -> plugin root
        templates/
        resources/
      references/    <- real directory, contains ONLY symlinks -> plugin root
```

**Rule 2: Use real mirrored directories + file-level symlinks inside the skill.**

The skill must have real (non-symlink) directories that mirror the structure. Inside those directories,
each individual file is a symlink pointing up to the plugin root copy:

```bash
# From skills/<skill-name>/scripts/
ln -s ../../../scripts/adr_manager.py adr_manager.py   # 3 levels up to plugin root

# From skills/<skill-name>/assets/templates/
ln -s ../../../../assets/templates/adr-template.md adr-template.md   # 4 levels up

# From skills/<skill-name>/references/
ln -s ../../../references/fallback-tree.md fallback-tree.md   # 3 levels up
```

DO NOT symlink entire directories. npx resolves file-level symlinks by copying the real content at
install time. Directory-level symlinks are silently dropped.

**Rule 3: SKILL.md files use relative paths from the skill root.**

Per the open Agent Skills spec (https://agentskills.io/specification), file references in SKILL.md
should use paths relative to the skill root — not hardcoded install locations:

```
# Correct - relative from skill root (portable, spec-compliant)
python scripts/adr_manager.py create ...

# Also acceptable for Claude Code agents running from project root
python .agents/skills/adr-management/scripts/adr_manager.py create ...

# Wrong - breaks when not in skill directory
python ./adr_manager.py create ...
```

Command files (`commands/*.md`) reference the installed path since they are not installed as part
of a skill and have no skill root to resolve from:
```
python .agents/skills/adr-management/scripts/adr_manager.py create ...
```

## Validated Test

Validated across 15+ plugins including: `task-manager`, `adr-manager`, `vector-db`, `rlm-factory`,
`rsvp-speed-reader`, `rlm-factory`, `plugin-manager`, `obsidian-integration`, `mermaid-to-png`,
`memory-management`, `markdown-to-msword-converter`, `link-checker`, `huggingface-utils`,
`exploration-cycle-plugin`, `excel-to-csv`, `context-bundler`.

**Pattern verified:**
- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)
- File-level symlink in skill (e.g. `skills/adr-management/scripts/adr_manager.py -> ../../../scripts/adr_manager.py`)
- After `npx skills add`: `.agents/skills/adr-management/scripts/adr_manager.py` is a real file (symlink resolved)

npx copies real content. The installed skill has working files, no broken symlinks.

## Consequences

**Positive:**
- One authoritative copy of every script, template, and reference document per plugin
- Commands and skills both get the same file at install time, regardless of install method
- npx install produces a working skill with real files (no broken symlinks in `.agents/`)
- SKILL.md script paths work correctly when agents invoke them from project root

**Negative:**
- Symlink depth must be calculated carefully per directory level (file count is low, manageable)
- Adding a new shared file requires: add to plugin root dir + add symlink in skill dir (two steps)

**Additional benefit: mirrored structure preserves relative path correctness.**

When the plugin root and skill directories share the same folder/subfolder structure for `references/`,
`assets/`, and `scripts/`, the relative paths embedded inside skill content files (e.g. SKILL.md
referencing `references/diagrams/foo.mmd`) remain valid both in the plugin source tree and after
`npx skills add` installs the skill. The symlinks inside the skill mirror the same depth as the real
files at plugin root, so any relative reference that works at plugin root also works from the skill
root without modification.

**Applies to all future plugins with shared resources.** Any plugin that has both `commands/` and
`skills/` with shared scripts/assets/references must follow this structure. Plugins with only skills and
no shared command references may keep resources inside the skill with no symlinks needed.

## Audit Tool

`plugins/agent-scaffolders/scripts/audit_plugin_structure.py` validates compliance with this ADR.
Run it against any plugin to detect real files inside skill directories that should be at plugin root:

```bash
python plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
```

Output:
- **ERROR**: real file found in `skills/<skill>/scripts|references|assets/` — must move to plugin root + symlink
- **WARNING**: symlink target resolves outside plugin root — depth calculation is wrong

Exit code 0 = clean, exit code 1 = violations found.

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Duplicate files in plugin root and skill | Violates zero-duplication principle; copies drift out of sync silently |
| Directory-level symlinks in skill | npx silently drops them; installed skill is broken |
| Keep resources only inside skill | Command file references break; no single source of truth |
| Post-install copy script | External tooling dependency; fragile; requires bridge plugin changes |
