---
name: obsidian-query-agent
description: Progressive-disclosure query interface for the Obsidian LLM wiki. Returns RLM summary first, expands to bullets, then full wiki node on demand.
---

# Obsidian Query Agent (obsidian-query-agent)

Provides a progressive-disclosure query interface for the Obsidian LLM wiki, delivering cheapest useful answers first.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Always query with `--level summary` first before requesting larger context windows or raw files.
- Use `--save-as` when newly synthesized knowledge should be filed back into the wiki.
- Store RLM caches under configured profile paths or `{wiki_root}/rlm/`.

## Dependencies

Requires Python 3.8+ and pyyaml.

## Quick start
```bash
# Query summary (default ~50 tokens)
python3 plugins/obsidian-wiki-engine/scripts/query_wiki.py --wiki-root <path> "concept-name"

# Expand to key idea bullets (~150 tokens)
python3 plugins/obsidian-wiki-engine/scripts/query_wiki.py --wiki-root <path> "concept-name" --level bullets

# Full wiki node with backlinks (~800 tokens)
python3 plugins/obsidian-wiki-engine/scripts/query_wiki.py --wiki-root <path> "concept-name" --level full
```

## Workflow
1. **Initial Lookup**: Run progressive query at summary level (`--level summary`) to obtain low-token answers.
2. **Context Expansion**: If insufficient, escalate disclosure to `--level bullets` or full node (`--level full`).
3. **Graph Backlinks**: Ingest bidirectional wikilinks to identify related concept clusters.
4. **Knowledge Filing**: If query produces new insights, save back to vault via `--save-as`.

## Verification
```bash
# Test query execution across disclosure levels
python3 plugins/obsidian-wiki-engine/scripts/query_wiki.py --wiki-root <path> "concept-name" --level summary

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-query-agent --mode source
```

## References
- [wiki-query-guide.md](references/wiki-query-guide.md) - Three-phase search strategy, filing loop, and vector DB options.
