# ADR-002: Multi-Skill Script Centralization

## Status
Proposed

## Context
Within the `agent-plugins-skills` monorepo, a single Plugin often contains multiple distinct Skills (e.g., the `plugin-manager` plugin contains `maintain-plugins`, `replicate-plugin`, and `bridge-plugin` skills). 

Historically, scripts that were shared across multiple skills within the *same* plugin were duplicated, or scattered randomly inside one skill's directory while other skills reached across internal boundaries to execute them. This caused maintenance headaches (updating a script required updating multiple copies) and broke the logical boundary of the consuming skills.

We need a standardized architectural rule defining exactly where Python scripts physically live when they support one skill vs. multiple skills within the same plugin boundary.

## Decision
**We mandate a Hub-and-Spoke model for internal plugin scripts, driven by usage scope.**

1. **Single-Skill Usage**: If a python script is exclusively used by a single skill, it must be physically located inside that specific skill's executable directory (`plugins/<plugin-name>/skills/<skill-name>/scripts/script.py`).
2. **Multi-Skill Usage**: If a python script is required by *two or more* skills within the same plugin, it must be factored out into the primary Plugin root (`plugins/<plugin-name>/scripts/script.py`). 
3. **Symlink Wiring**: The consuming skills must not execute the root script via backward relative paths (e.g., `python ../../scripts/foo.py`). Instead, they must maintain a local symlink within their own territory (`skills/<skill-name>/scripts/foo.py -> ../../../scripts/foo.py`) and execute the symlink locally.

## Consequences
**Positive:**
- Enforces strict DRY (Don't Repeat Yourself) within a plugin's boundary.
- All CLI commands and execution strings across `SKILL.md` workflows remain perfectly uniform and localized (`python ./scripts/foo.py`), oblivious to whether the script is physical or a symlink to the root repo.
- The `plugins/<plugin-name>/scripts/` folder serves as a clear "shared library" for internal capability logic.

**Negative:**
- Generating a new shared script requires a structural setup step to wire the relative symlinks into the consuming `skills/` directories.
- Move/Rename refactoring requires careful attention to avoid breaking the relative symlinks.

## Alternatives Considered
- **Code Duplication**: Keeping physical copies of scripts in every skill that needs them. Rejected because bug fixes are easily missed across the duplicate copies.
- **Root-Only Scripts**: Forcing *all* scripts into the plugin root `scripts/` directory, regardless of usage. Rejected because it crowds the root directory with highly specialized, single-use scripts that belong conceptually with their specific skill.
