---
description: "Run a semantic health check over the LLM wiki."
argument-hint: "[--wiki-root <path>] [--json]"
---

# /wiki-lint

Performs semantic checks to find inconsistencies, missing concepts, stale articles, and new article candidates in the wiki.

Runs `scripts/lint_wiki.py` under the hood. For detailed specifications and the full execution protocol, see `skills/obsidian-wiki-linter/SKILL.md`.
