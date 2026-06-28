---
description: "Audit the Obsidian LLM wiki for orphaned nodes, missing RLM summaries, stale source files, and broken wikilinks."
argument-hint: "[--wiki-root <path>] [--fix-stale] [--json]"
---

# /wiki-audit

Audits the wiki for orphans, missing summaries, and stale content.

Runs `scripts/audit.py` under the hood. For detailed specifications and the full execution protocol, see `skills/obsidian-wiki-builder/SKILL.md`.
