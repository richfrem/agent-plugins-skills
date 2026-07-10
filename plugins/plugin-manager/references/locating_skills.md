Locating where a skill is registered in this repository

This short reference explains the canonical places to look when you want to
find where a skill is declared, packaged, or wired into the installer
inventory inside the agent-plugins-skills monorepo.

1) plugin.yaml (plugin manifest)
   - Path: plugins/<plugin>/plugin.yaml
   - Purpose: Declares which skills the plugin exposes. If a skill appears here
     it is part of the plugin's public surface and will be considered by the
     bridge installer.

2) SKILL.md (canonical skill file)
   - Path: plugins/<plugin>/skills/<skill>/SKILL.md
   - Purpose: The human- and machine-readable skill definition. Contains
     usage, dependencies, scripts, and any instructions the installer or
     users should follow.

3) symlinks.json (packaging / build inventory)
   - Path: ${REPO_ROOT}/symlinks.json
   - Purpose: Lists file-level symlink rules used by the repo packaging system
     and the installer test harness. If scripts or SKILL.md entries are
     referenced here they are intended to be mirrored or symlinked into
     skill-level paths during packaging.

4) skills-lock.json (project lock)
   - Path: ${REPO_ROOT}/skills-lock.json
   - Purpose: Lockfile tracking skills packaged for distribution. Non-empty
     entries indicate the skill was recorded for installs.

5) README / commands / agents / tasks
   - Purpose: Various higher-level docs and agent definitions often reference
     skills by name. Use these to understand intended usage, verification
     commands, or installation checks (e.g. `ls .agents/skills/<skill>/` checks).

Quick grep examples

  # List plugin.yaml files that mention the skill
  git grep "obsidian-wiki-builder" -- plugins || true

  # Show the skill's SKILL.md
  sed -n '1,120p' plugins/obsidian-wiki-engine/skills/obsidian-wiki-builder/SKILL.md

User-interaction note (installer privacy & search scope)

  - When running repo-scoped searches or installer discovery, the agent MUST
    confirm the search scope with the user and echo the selected scope before
    executing any filesystem-wide probe. Example: "Searching only
    /Users/me/projects/agent-plugins-skills — proceed? (Y/n)".
  - Default practice: prefer repo-scoped inspections when the user expresses
    repository context. Avoid scanning the whole disk unless explicitly
    requested.

This file is intentionally concise — add examples or local-check commands
here when a session surfaces a new helpful probe or verification script.
