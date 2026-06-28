---
description: "Full rebuild of the LLM wiki from scratch."
argument-hint: "[--wiki-root <path>] [--force]"
---

# /wiki-rebuild

Triggers a complete pipeline rebuild: purges existing nodes, re-reads all registered raw sources, compiles them, and refreshes the RLM layers.

Runs `scripts/wiki_builder.py` under the hood. For detailed specifications and the full execution protocol, see `skills/obsidian-wiki-builder/SKILL.md`.
