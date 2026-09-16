---
description: Universal rules for plugin file duplication, symlinks, cross-plugin resource bounds, Python script organization, and relative execution paths.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/**/*.py", "plugins/**/*.md"]
---

# Plugin Architecture & Coupling Policy

## 1. Hub-and-Spoke Resource Model & Installer Dereferencing

1. **Authoring Model vs. Runtime Model**:
   ```text
   one canonical editable source
   → managed file-level symlinks in skill source folders
   → plugin installer dereferences symlinks into hard copies
   → installed skills are fully self-contained
   ```
   Symlinks are used exclusively as a repository authoring and maintenance mechanism. The plugin installer dereferences all symlinks into physical hard copies during deployment into `.agents/`.

2. **Self-Contained Installed Skills**:
   An installed skill must be fully portable and independent. It must **NEVER** depend at runtime on:
   - The source repository or source symlink
   - The source plugin directory
   - The repository root or monorepo environment
   - Another installed plugin
   - A sibling Python distribution or external runtime package

3. **Canonical Ownership**:
   Every shared resource has exactly one editable canonical source owner in the repository. Consumers receive installer-materialized hard copies, which are deployed artifacts—not editable authorities. Do not create competing canonical source copies.

---

## 2. Separation of Concerns & Loose Coupling

1. **Pluggable Independence**: If a user installs a skill via `plugin_add.py` or `uvx`, that skill MUST function completely in isolation. It cannot crash or halt because another plugin is uninstalled or missing.
2. **Agent Delegation over Code Interfaces**: If a plugin requires coordination with another plugin, it must do so via Natural Language agent instructions (e.g., *"Please invoke the `<plugin>-agent` to..."*) rather than hardcoded Python imports, hidden filesystem state manipulations, or rigid cross-plugin bindings.
3. **Cross-Plugin Wire Contracts**: Sharing schemas, references, assets, or executable contract helpers through installer-materialized hard copies is permitted. Cross-plugin Python runtime imports or cross-plugin directory symlinks are strictly forbidden.

---

## 3. Plugin-Level Resource & Python Organization

1. **One Canonical Plugin-Level `scripts/` Directory**:
   Canonical Python code shared by skills belongs at the plugin root under `plugins/<plugin>/scripts/`.
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

---

## 4. Resource Placement by Purpose

Resource placement is determined strictly by **purpose**, not file extension:

| Directory | Purpose |
|---|---|
| `references/` | Schemas, contracts, and documentation the agent reads |
| `scripts/` | Executable Python, validation, transformation, and helper scripts |
| `assets/` | Templates and static resources copied, embedded, transformed, or emitted |
| `tests/fixtures/` | Plugin test evidence and test fixtures |
| `evals/fixtures/` | Skill evaluation evidence and test cases |

---

## 5. Mandatory Symlink Workflow & Cross-Platform Protocol

**NEVER create symlinks with `ln -s` directly.**  
**NEVER create real file copies where a symlink should exist.**

All symlink creation, repair, and auditing must go through `.agents/skills/symlink-manager/scripts/symlink_manager.py` and be recorded in `symlinks.json`.

1. **File-Level Symlinks ONLY**:
   All shared resources within or across plugins must use **file-level symlinks ONLY**. Directory-level symlinks are strictly forbidden because installation bridges drop them or fail on cross-platform checkouts.
2. **Zero Manual `ln -s`**:
   Never invoke `ln -s` directly in the shell. Direct calls bypass the manifest, causing links to fail or disappear on fresh checkouts.
3. **Canonical Source Locations**:
   | Resource Type | Canonical Master Copy | Installed / Spoke Location |
   |---|---|---|
   | Python scripts | `plugins/<plugin-name>/scripts/` | `plugins/<plugin-name>/skills/<skill>/scripts/` |
   | References / docs | `plugins/<plugin-name>/references/` | `plugins/<plugin-name>/skills/<skill>/references/` |
   | Assets / templates | `plugins/<plugin-name>/assets/` | `plugins/<plugin-name>/skills/<skill>/assets/` |
4. **Required 5-Step Symlink Workflow**:
   - **Step 1: Diagnose first**
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
     Identify every `? regular file (not a link)` and `✗ broken symlink` before touching anything.
   - **Step 2: Remove real-file imposters**
     If a file that should be a symlink is a regular file copy, delete the imposter first:
     ```bash
     rm -f path/to/real-file-that-should-be-symlink
     ```
   - **Step 3: Register link in manifest (`symlinks.json`)**
     Record the canonical source and skill target via `symlink_manager.py` or formatted entry:
     `{ "src": "canonical/source.py", "dst": "skill/scripts/source.py", "strategy": "symlink", "description": "..." }`
   - **Step 4: Restore all from manifest**
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore
     ```
   - **Step 5: Verify clean status**
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
     Ensure zero `? regular file` or `✗ broken symlink` entries remain before committing.

---

## 6. Strict Relative Path Execution

1. **Relative to Skill Root**: Inside `SKILL.md` workflows, path references must always be **relative to the skill root** (e.g., `../scripts/script.py` or `python3 scripts/script.py`). **Never use absolute paths or paths relative to the repository root.**
2. **Self-Contained Content**: Every file a skill references must be present inside the skill's directory — either as a hard copy or a symlink.
3. **Execution Context**:
   Installed skills execute from dynamic target locations:
   - `.agents/skills/<skill-name>/` (canonical)
   - `.claude/skills/<skill-name>/`
   Relative paths inside commands resolve from the skill root at the installed location. Verify paths against the installed structure, not the source tree.
