---
concept: adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks
source: plugin-code
source_file: /Users/richardfremmerlid/Projects/agent-plugins-skills/ADRs/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.623893+00:00
cluster: plugin-code
content_hash: 1e84e516ccc7ceb4
---

# ADR-003: Plugin Skill Resource Sharing via Mirrored Folder Structure and File-Level Symlinks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
SKILL.md files that invoke scripts as `python3 ./adr_manager.py` fail when the agent runs from the
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
install time. Directory-level symlink

*(content truncated)*

## See Also

- [[adr-005-plugin-separation-of-concerns-and-loose-coupling]]
- [[adr-005-plugin-separation-of-concerns-and-loose-coupling]]
- [[adr-005-plugin-separation-of-concerns-and-loose-coupling]]
- [[adr-005-plugin-separation-of-concerns-and-loose-coupling]]
- [[adr-manager-plugin]]
- [[canonical-agentic-os-file-structure]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `/Users/richardfremmerlid/Projects/agent-plugins-skills/ADRs/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md`
- **Indexed:** 2026-04-17T06:42:09.623893+00:00
