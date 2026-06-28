---
description: "Build Karpathy-style wiki nodes from raw sources."
argument-hint: "[--source label] [--rlm-cache-dir path] [--dry-run]"
---

# /wiki-build

Runs the full wiki node build pipeline: ingest raw sources, extract and merge concepts across sources, and format Karpathy-style wiki nodes.

Runs `scripts/wiki_builder.py` under the hood. For detailed specifications and the full execution protocol, see `skills/obsidian-wiki-builder/SKILL.md`.
