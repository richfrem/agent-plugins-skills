---
description: Universal rules for plugin file duplication, symlinks, and cross-plugin dependency bounds.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/*.py"]
---

## 🏛️ Plugin Architecture & Symlink Rules (Summary)

**Full ADR context → `ADRs/001_` through `004_`**

### Non-Negotiables
1. **Zero Duplication (Hub-and-Spoke)**: Shared scripts, assets, and templates within a plugin must live exactly *once* at the plugin's root (`plugins/<plugin-name>/scripts/` or `assets/`). Do not duplicate files across skills within the same plugin.
2. **File-Level Symlinks ONLY**: You must use **file-level symlinks ONLY** to share resources within a skill (e.g., `ln -s ../../../scripts/script.py script.py`). Directory-level symlinks are strictly forbidden because `npx` drops them during installation.
3. **No Brittle Cross-Plugin Script Paths**: Sibling plugins cannot execute scripts from one another at runtime using relative paths (e.g. `../../other-plugin/`). Skills must remain entirely self-contained at deployment time. If you need functionality from another plugin at runtime, use **Agent Skill Delegation** (tell the agent to trigger the other skill).
4. **Relative Path Execution**: Inside `SKILL.md` workflows, path references must always be **relative to the skill root** (e.g., `python scripts/script.py` rather than absolute paths or backwards traversals), ensuring flawless portability regardless of exactly where the `.agents/` folder or environment resides.
