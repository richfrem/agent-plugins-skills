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
   This keeps both goals of the model: **one physical copy in source**, and **a physical copy in every skill that needs it** after install. Skill source folders hold no symlink objects. The build is `plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/apm_build_pipeline.py --pack`.

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

## 5. Self-Contained Skills & Resource Sharing

**NEVER create new symlinks** (`ln -s` or otherwise). Raw filesystem symlinks are strictly prohibited.

1. **Self-Contained Skills (End State)**:
   Every skill must be fully self-contained. Scripts, references, assets, tests, and evals live directly within the skill directory (`plugins/<plugin>/skills/<skill>/`). There are no shared plugin-root `scripts/`, `references/`, `assets/`, or `tests/`.
2. **One Owning Skill & Cross-Skill Delegation**:
   When a skill needs functionality implemented in another skill, the code lives in the single owning skill. Cross-skill interaction happens through skill invocation by name (prompt loop), never through cross-skill relative imports or relative script execution paths.
3. **No Climbing Paths in Code**:
   Paths in code blocks, inline code, or execution commands that climb out of the skill directory (e.g. `../../scripts/tool.py`) are prohibited. Scripts run only within their own skill boundary or call standard CLI tools on PATH.
4. **Transition Manifest (Legacy Plugins)**:
   Plugins actively migrating to the self-contained standard may transitionally utilize the copy manifest (`symlinks.json`, `strategy: "copy"`). Fully consolidated plugins have 0 manifest entries and zero plugin-root shared files.
5. **Verify Before Committing**:
   Run `audit_skill.py --mode source` on every skill and `audit_plugin_structure.py` on the plugin root. For plugins still using the transitional copy manifest, run `materialize_copies.py --check`.

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
   | Another skill or agent | Its name: "use the `managing-adrs` skill" |
   | A file in the same skill | A path relative to the skill folder (`scripts/tool.py`, `references/guide.md`) |
   | A document elsewhere in the plugin | A markdown link (Section 5.2) |
   | Another plugin's capability | Its skill or agent by name |
3. **Never use** absolute paths, repository-root paths, or install-folder paths (`.agents/`, `.claude/`, `~/.apm/`, `apm_modules/`) in `SKILL.md`, references, agents or hook commands.
