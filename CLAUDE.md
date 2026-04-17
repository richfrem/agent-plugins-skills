# CLAUDE.md

## Purpose

Upstream source monorepo for a cross-platform library of reusable AI agent plugins and skills.
Plugins are authored here and deployed into target projects via the bridge installer.
Individual skills must be **fully self-contained** — no runtime cross-plugin dependencies.

## Key Commands

```bash
# Install plugins into any project (recommended)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Interactive local install
python plugins/plugin-manager/scripts/plugin_add.py

# Bulk install all plugins
python plugins/plugin-manager/scripts/install_all_plugins.py
```

> **Windows**: Never use `npx skills add` — use `uvx` or `bootstrap.py` instead.

```bash
# Dependencies (per plugin)
pip-compile ./requirements.in && pip install -r ./requirements.txt
```

## Architecture

```
plugins/<plugin>/           ← canonical source
  skills/<skill>/SKILL.md   ← skill definition
  evals/evals.json          ← routing evals (should_trigger boolean schema)
  scripts/                  ← shared scripts (file-level symlinks only)
  agents/ commands/         ← sub-agents and slash commands

.agents/                    ← bridge installer output (hard copies, symlinks resolved)
  skills/ agents/ workflows/
```

See `plugins/plugin-manager/scripts/` for ecosystem management scripts.
See `ADRs/` for authoritative architecture rules.

## Coding Rules (always applied)

- **ADR-001**: No cross-plugin script execution — delegate via agent skill at runtime
- **ADR-002**: Within-plugin multi-skill script sharing via hub-and-spoke (plugin root `scripts/`)
- **ADR-003**: File-level symlinks only — never directory symlinks, never duplicate files
- **ADR-004**: Installed artifacts must be self-contained — no runtime cross-plugin paths

## Skill Standards (always applied)

- Skill `name`: kebab-case, matches directory name exactly, 1–64 chars
- Skill `description`: third person ("Extracts text", not "I extract text")
- `evals.json`: must use `should_trigger: true/false` — legacy `expected_behavior` produces 0% accuracy
- SKILL.md: under ~500 lines; extra detail goes in `references/` files
- Helper scripts: Python only — never generate `.sh` bash scripts

## Scaffolding New Plugins/Skills

Use these skills rather than hand-rolling structure:
- `create-plugin` — full plugin scaffold with discovery interview
- `create-skill` — skill scaffold with evals, references, acceptance-criteria
- `audit-plugin` — validate structure after scaffolding

Then run `plugin_add.py` to deploy.

## Scratch Output

Write temporary files and analysis output to `temp/` — never to the project root directly.

## Context Retrieval & Search Protocol (Super-RAG)

Before reading source files blindly using expensive grep or wandering the codebase, you **MUST** follow the 3-Phase Search Protocol:
1. **Phase 1 (Keyword/O(1))**: Run `/rlm-factory:search "term"` (or `rlm-search` from scripts) to query the distilled `.agent/learning/rlm_wiki_cache` for ultra-fast, token-efficient architecture context.
2. **Phase 2 (Semantic/O(log N))**: Run `/vector-db:search "term"` (or use the vector-db python scripts) for deep semantic code retrieval if Phase 1 directs you to a core concept but lacks the exact payload.
3. **Phase 3 (Concept/Exact)**: Use `/wiki-query "concept"` to pull final cohesive Karpathy-style documentation nodes from the `.wiki` root.

*Only fall back to raw grep if the hierarchical Super-RAG caches miss entirely.*
