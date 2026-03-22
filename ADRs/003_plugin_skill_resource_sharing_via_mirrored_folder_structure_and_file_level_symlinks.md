# ADR-003: Plugin Skill Resource Sharing via Mirrored Folder Structure and File-Level Symlinks

## Status
Accepted - Validated

Tested on two plugins (`task-manager` and `adr-manager`). Both installed correctly via
`npx skills add` with all symlinks resolved to real files. Approach confirmed working.

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

**Failure 3: Relative path `./script.py` breaks from project root.**
SKILL.md and command files that invoke scripts as `python3 ./adr_manager.py` fail when the agent runs
from the project root (which is always). Scripts must be referenced by their installed root-relative path
`.agents/skills/<skill-name>/scripts/<script>.py`.

## Decision

**Rule 1: Scripts, assets, and references live at plugin root - one copy only.**

When a plugin contains both `commands/` and `skills/`, all shared resources belong at the plugin root:

```
plugins/<plugin-name>/
  scripts/           <- real directory, canonical source
  assets/            <- real directory, canonical source
    templates/
  references/        <- real directory, canonical source
  commands/
    <command>.md     <- references .agents/skills/<name>/scripts/... paths
  skills/
    <skill-name>/
      scripts/       <- real directory (mirrored), contains only symlinks
      assets/        <- real directory (mirrored), contains only symlinks
        templates/
      references/    <- real directory (mirrored), contains only symlinks
      SKILL.md
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

**Rule 3: SKILL.md and command files reference the installed root-relative path.**

```
# Correct
python3 .agents/skills/adr-management/scripts/adr_manager.py create ...

# Wrong - breaks from project root
python3 ./adr_manager.py create ...
```

## Validated Test

Tested on the `task-manager` plugin (task-agent skill) and `adr-manager` plugin (adr-management skill).

**Setup:**
- Real file: `plugins/task-manager/assets/templates/task-template.md` (596 bytes)
- Symlink: `plugins/task-manager/skills/task-agent/assets/templates/task-template.md`
  -> `../../../../assets/templates/task-template.md`

**Install:**
```bash
npx skills add ./plugins/task-manager --yes --force
```

**Result:**
```
.agents/skills/task-agent/assets/templates/task-template.md   <- 596 bytes (real file, symlink resolved)
```

npx copied the real content. The installed skill has working files, not broken symlinks.

**adr-manager plugin restructure (first full plugin to apply this ADR):**
- Moved `skills/adr-management/scripts/`, `assets/`, `references/` to plugin root
- Created real mirrored directories in skill with file-level symlinks
- Updated SKILL.md and commands/adr-management.md to use `.agents/skills/adr-management/scripts/` paths

## Consequences

**Positive:**
- One authoritative copy of every script, template, and reference document per plugin
- Commands and skills both get the same file at install time, regardless of install method
- npx install produces a working skill with real files (no broken symlinks in `.agents/`)
- SKILL.md script paths work correctly when agents invoke them from project root

**Negative:**
- Symlink depth must be calculated carefully per directory level (file count is low, manageable)
- Adding a new shared file requires: add to plugin root dir + add symlink in skill dir (two steps)

**Applies to all future plugins with shared resources.** Any plugin that has both `commands/` and
`skills/` with shared scripts/assets/references must follow this structure. Plugins with only skills and
no shared command references may keep resources inside the skill with no symlinks needed.

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Duplicate files in plugin root and skill | Two copies drift out of sync; maintenance burden |
| Directory-level symlinks in skill | npx silently drops them; installed skill is broken |
| Keep resources only inside skill | Command file references break; no single source of truth |
| Post-install copy script | External tooling dependency; fragile; requires bridge plugin changes |
