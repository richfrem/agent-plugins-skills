---
concept: procedural-fallback-tree-memory-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/memory-management/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.118392+00:00
cluster: file
content_hash: d2e75d9a4b5e2cb3
---

# Procedural Fallback Tree: Memory Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Memory Management

## 1. Hot Cache File Missing at Boot
If a configured hot cache file (primer, boot digest, boot contract, or snapshot) is not found at the configured path:
- **Action**: Report the missing file by path. Do NOT silently skip it or continue as if context was loaded. Load the remaining files and flag the session as "partial boot" until the user resolves the missing file.

## 2. Snapshot File Stale (Integrity Failure)
If the snapshot file has not been updated since the last session seal:
- **Action**: Flag the snapshot as stale at boot. Load it anyway but mark all entries with a staleness warning. Ask user to confirm context before acting on any snapshot entry that may be outdated.

## 3. Demotion Target Directory Missing
If the configured `MEMORY_DESIGN_DIR`, `MEMORY_DOMAIN_DIR`, or `MEMORY_GOVERNANCE_DIR` does not exist:
- **Action**: Report the missing directory. Do NOT silently create it without confirmation. Ask the user if it should be created before proceeding with the demotion.

## 4. Tool Inventory / RLM Summary Ledger Unavailable
If the semantic cache (`MEMORY_TOOL_CACHE`) or vector store is unavailable:
- **Action**: Skip tiers 3 and 4 of the lookup flow. Report that semantic search is unavailable. Do NOT fail the session — fall back to asking the user directly.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-dependency-management]]
- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-dependency-management]]
- [[procedural-fallback-tree-dependency-management]]
- [[procedural-fallback-tree-agent-swarm]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/memory-management/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.118392+00:00
