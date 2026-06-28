---
description: "Parse all registered raw source directories and build Karpathy-style wiki nodes."
argument-hint: "[--wiki-root <path>] [--source <label>] [--force] [--dry-run]"
---

# /wiki-ingest

Parses raw sources registered in `wiki_sources.json` and updates `agent-memory.json` with their hashes.

Runs `scripts/ingest.py` under the hood. For detailed specifications and the full execution protocol, see `skills/obsidian-wiki-builder/SKILL.md`.
