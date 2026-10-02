---
name: obsidian-rlm-distiller
description: Distills wiki source files into the three-layer RLM summary structure (summary.md, bullets.md, deep.md) using cheap cloud LLM CLIs. Routes to mini/flash tiers.
---

# Obsidian RLM Distiller (obsidian-rlm-distiller)

Distills wiki source files into a three-layer RLM summary structure using low-cost cloud LLM CLIs.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Route strictly to mini/flash tier models (`gpt-5-mini`, `claude-haiku-4-5`, `gemini-3-flash-preview`); never use local models.
- Track source file hashes to prevent redundant re-distillation of unchanged notes.
- Every distilled concept must output the standard 3-tier structure (`summary.md`, `bullets.md`, `deep.md`).

## Dependencies

Requires Python 3.8+ and at least one CLI installed: `copilot`, `claude`, or `gemini`.

## Quick start
```bash
# Distill all stale wiki nodes
python3 plugins/obsidian-wiki-engine/scripts/distill_wiki.py --wiki-root <path>

# Distill single named source
python3 plugins/obsidian-wiki-engine/scripts/distill_wiki.py --wiki-root <path> --source arch-docs

# Dry run inspection
python3 plugins/obsidian-wiki-engine/scripts/distill_wiki.py --wiki-root <path> --dry-run
```

## Workflow
1. **Source Discovery**: Scan registered wiki sources and compare hashes against `meta/agent-memory.json`.
2. **Model Routing**: Select lowest-cost available CLI runner (`copilot` -> `claude` -> `agy`).
3. **Multi-Tier Distillation**: Generate 1-paragraph summary, 6-bullet key points, and comprehensive deep summary.
4. **Cache Persistence**: Store outputs in `{wiki_root}/rlm/<concept>/` and update hash registry.

## Verification
```bash
# Verify distillation with dry run
python3 plugins/obsidian-wiki-engine/scripts/distill_wiki.py --wiki-root <path> --dry-run

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-rlm-distiller --mode source
```

## References
- [wiki-distillation-guide.md](references/wiki-distillation-guide.md) - Summary schemas, cache colocation, and runner configurations.
