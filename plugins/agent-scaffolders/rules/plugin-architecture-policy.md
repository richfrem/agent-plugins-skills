---
description: Universal rules for plugin file sharing, the copy manifest, cross-plugin resource bounds, Python script organization, and install-location-independent references under APM.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/**/*.py", "plugins/**/*.md"]
---

# Plugin Architecture & Coupling Policy

Plugins are installed with [APM](https://github.com/microsoft/apm) (see `docs/plans/apm_migration_plan.md`). Behaviour cited here was verified with APM `0.33.0`.

## 1. Hub-and-Spoke Resource Model & Build-Time Copies

1. **Authoring Model vs. Runtime Model**:
   ```text
   one canonical editable source file
   → copy manifest (symlinks.json, strategy "copy") lists the skill paths that need it
   → build pipeline creates physical copies in build/staging/ and packs a bundle
   → APM installs the bundle; every installed skill is fully self-contained
   ```
   This keeps both goals of the model: **one physical copy in source**, and **a physical copy in every skill that needs it** after install. Skill source folders hold no symlink objects. The build is `plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/apm_build_pipeline.py --pack`.

2. **Self-Contained Installed Skills**:
   An installed skill must be fully portable and independent. It must **NEVER** depend at runtime on:
   - The source repository, the source plugin directory, or the repository root
   - Another installed plugin
   - A sibling Python distribution or external runtime package
   - A particular install location (project or global, any harness)

3. **Canonical Ownership**:
   Every shared resource has exactly one editable canonical source owner in the repository. Build-time copies are deployed artifacts, not editable authorities. Do not create competing canonical source copies.

---

## 2. Separation of Concerns & Loose Coupling

1. **Pluggable Independence**: A skill installed with APM (alone, with `--skill`, or as part of its plugin) MUST function completely in isolation. It cannot crash or halt because another plugin is uninstalled or missing.
2. **Agent Delegation over Code Interfaces**: If a plugin requires coordination with another plugin, it must do so via natural-language agent instructions (e.g., *"Please invoke the `<plugin>-agent` to..."*) rather than hardcoded Python imports, hidden filesystem state manipulations, or rigid cross-plugin bindings.
3. **Cross-Plugin Wire Contracts**: Sharing schemas, references, assets, or executable contract helpers is permitted only through the copy manifest within a plugin, or by delegation across plugins. Cross-plugin Python runtime imports, cross-plugin links and cross-plugin symlinks are strictly forbidden. APM aborts an install on a symlink that leaves the package, and leaves links that leave the plugin unresolved.

---

## 3. Plugin-Level Resource & Python Organization

1. **One Canonical Plugin-Level `scripts/` Directory**:
   Canonical Python code shared by skills belongs at the plugin root under `plugins/<plugin>/scripts/`, listed in the copy manifest for each skill that runs it.
2. **Logical Subfolders Approved**:
   Related Python scripts may be logically grouped into cohesive subfolders beneath `scripts/`.
   Approved examples:
   - `scripts/contracts/` (plugin-owned contracts and validation)
   - `scripts/pandoc_fixes/` (cohesive implementation modules)
   - `scripts/validation/` (input/output validation scripts)
   - `scripts/media/` (media conversion and handling)
3. **No Redundant Package-Name Directory**:
   Do **NOT** add a redundant package-name directory inside `scripts/` (e.g. `scripts/<plugin_name>/...`). The enclosing plugin directory already establishes the domain context.
4. **No Top-Level Sibling Runtime Packages**:
   Top-level external runtime packages (e.g. `contracts/python/` or `runtime/python/`) must not exist as required external dependencies. All shared code must belong to an owning plugin.
5. **Hook Scripts**: Hook commands in `hooks/hooks.json` reference scripts as `${CLAUDE_PLUGIN_ROOT}/<path>`. APM copies the folder a hook script lives in into each harness, so keep hook scripts in a small dedicated `hooks/` folder. Hook scripts run under every target harness: use `Path(__file__)` for their own files and a harness-neutral project path (e.g. `context/`) for state, never `.claude/` or `.agents/`.
6. **Plugin Package Manifests**:
   - `apm.yml`: The primary package manifest at `plugins/<plugin>/apm.yml` specifying package name (`@richfrem/<plugin>`), version, description, and client targets (`claude,copilot,codex,antigravity`).
   - `.claude-plugin/plugin.json`: Secondary compatibility manifest with minimal metadata schema; `author` must be an object `{"name": "...", "email": "..."}`.
   - **Zero Legacy Plumbing**: `.claude-plugin/marketplace.json`, `gemini-extension.json`, and `.agents/ownership/` are retired legacy constructs and must not be created in new or updated plugins.

---

## 4. Resource Placement by Purpose

Resource placement is determined strictly by **purpose**, not file extension:

| Directory | Purpose |
|---|---|
| `references/` | Schemas, contracts, and documentation the agent reads |
| `scripts/` | Executable Python, validation, transformation, and helper scripts |
| `assets/` | Templates and static resources copied, embedded, transformed, or emitted |
| `hooks/` | Agent runtime hook scripts and `hooks.json` |
| `tests/fixtures/` | Plugin test evidence and test fixtures |
| `evals/fixtures/` | Skill evaluation evidence and test cases |

A plugin's `rules/` folder is **not** deployed by APM. Rules are copied into a project's `.agent/rules/` by setup when required, and `AGENTS.md` lists them there.

---

## 5. Sharing Files Between Skills: Copy Manifest, Links, No New Symlinks

**NEVER create new symlinks** (`ln -s` or otherwise).
**NEVER commit a duplicate copy of a canonical file** into a skill folder.

1. **Scripts, assets and other files a skill uses directly** are shared through the **copy manifest**: one canonical file at the plugin root, plus one `symlinks.json` entry per skill that needs a copy:
   ```json
   { "src": "plugins/<plugin>/scripts/tool.py", "dst": "plugins/<plugin>/skills/<skill>/scripts/tool.py", "strategy": "copy", "description": "..." }
   ```
   The build pipeline creates each `dst` as a physical copy in `build/staging/` only. Plugins that use copy entries are distributed as the packed bundle (`build/dist/<plugin>-<version>.zip`); installing the raw git path or `./plugins/<plugin>` would not contain the copies.
2. **Documents a skill only reads** may instead be cited with a markdown link to the canonical file anywhere in the same plugin (e.g. `[Guide](../../references/guide.md)`). APM rewrites markdown links that leave the skill to point into its package cache, so they resolve for every harness, project and global. This avoids a copy entirely.
3. **Paths in code are not rewritten.** Paths in code blocks, inline code or plain text that climb out of the skill folder (e.g. `python3 ../../scripts/tool.py`) break after install. A script the skill runs must be present in the skill (as a copy-manifest entry if shared).
4. **One owning skill** is the alternative when a skill genuinely depends on another skill's behaviour: keep the script in the owning skill and have other skills use that skill by name.
5. **Materialize after cloning**: the copies are not in git. Run `materialize_copies.py` (convert-plugin-to-apm skill) after cloning and after changing a canonical file; it writes every copy into the working tree and lists them in the local git exclude file. Tests and local runs then see the same files an installed skill has. Edit the canonical file, never a copy; `materialize_copies.py --check` reports drifted copies.
6. **Verify before committing**: run `materialize_copies.py --check` and the build pipeline on the changed plugin. The pipeline reports missing copy sources, broken links and unrewritten paths, each with its standard fix.

---

## 6. Install-Location-Independent References

Installed skills run from different folders per harness and per install scope. Never name an install folder in instructions.

1. **Where APM installs** (targets `claude,copilot,agy,codex`):
   | Primitive | Project install | Global install |
   |---|---|---|
   | Skills | `.claude/skills/`, `.agents/skills/` (copilot, codex, agy) | `~/.claude/skills/`, `~/.agents/skills/`, `~/.gemini/antigravity-cli/skills/` |
   | Agents | `.claude/agents/`, `.github/agents/`, `.codex/agents/` | `~/.claude/agents/`, `~/.copilot/agents/`, `~/.codex/agents/` |
   | Hooks | merged into each harness's hook settings | same, at user level (not agy) |
   | Package cache | `apm_modules/` | `~/.apm/` |
2. **How to refer to things**:
   | Reference to | Write it as |
   |---|---|
   | Another skill or agent | Its name: "use the `adr-management` skill" |
   | A file in the same skill | A path relative to the skill folder (`scripts/tool.py`, `references/guide.md`) |
   | A document elsewhere in the plugin | A markdown link (Section 5.2) |
   | Another plugin's capability | Its skill or agent by name |
3. **Never use** absolute paths, repository-root paths, or install-folder paths (`.agents/`, `.claude/`, `~/.apm/`, `apm_modules/`) in `SKILL.md`, references, agents or hook commands.
