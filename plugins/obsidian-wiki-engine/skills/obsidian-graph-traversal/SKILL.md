---
name: obsidian-graph-traversal
plugin: obsidian-wiki-engine
description: "Semantic link traversal for Obsidian Vaults. Builds an in-memory graph index from wikilinks and provides instant forward-link, backlink, and multi-degree connection queries. Use when exploring note relationships or finding orphaned notes."
allowed-tools: Bash, Read
---

# Obsidian Graph Traversal (obsidian-graph-traversal)

Constructs an in-memory graph index from vault wikilinks to query forward links, backlinks, and multi-degree connection paths.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Read-Only Traversal**: Graph query and index construction operations must never modify vault note files.
- **Timestamp Cache Invalidation**: The `.graph-index.json` cache must automatically invalidate and re-index notes whose `mtime` has changed.
- **Embed Distinction**: Disambiguate semantic links (`[[Note]]`) from embed transclusions (`![[Note]]`) to prevent false graph edges.
- **Query Performance**: Traversal operations must return within a sub-2-second budget across vaults with 1,000+ notes.

## Dependencies

Requires `obsidian-parser` and Python 3.8+ (standard library only for traversal operations).

## Quick start

```bash
# Build the graph index for a vault
python3 plugins/obsidian-wiki-engine/scripts/graph_ops.py build --vault-root <vault-path>

# Query backlinks for a specific note
python3 plugins/obsidian-wiki-engine/scripts/graph_ops.py backlinks --note "Note Name"

# Find orphaned notes without incoming or outgoing links
python3 plugins/obsidian-wiki-engine/scripts/graph_ops.py orphans --vault-root <vault-path>
```

## Workflow

1. **Phase 1: Index Building**: Parse vault notes via `obsidian-parser`, extract wikilinks, and cache adjacency lists in `.graph-index.json`.
2. **Phase 2: Topology Querying**: Execute forward-link, backlink, or multi-degree connection traversals from the in-memory graph.
3. **Phase 3: Orphan & Cluster Detection**: Identify isolated notes lacking connections or discover tightly coupled concept clusters.
4. **Phase 4: Impact Evaluation**: Assess upstream and downstream dependencies before executing multi-file refactoring operations.

## Verification

```bash
# Verify graph CLI commands
python3 plugins/obsidian-wiki-engine/scripts/graph_ops.py build --help

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-graph-traversal --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - Graph traversal invariants and performance targets.
- [fallback-tree.md](references/fallback-tree.md) - Recovery procedures for missing indices or cyclic link paths.
