---
concept: acceptance-criteria-obsidian-graph-traversal
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-graph-traversal/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.125520+00:00
cluster: index
content_hash: 653962cb606cefbf
---

# Acceptance Criteria: Obsidian Graph Traversal

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Obsidian Graph Traversal

## 1. Index Freshness
- [ ] Agent always checks index freshness (mtime comparison) before any query.
- [ ] A stale or missing index triggers a rebuild before results are returned.
- [ ] Rebuild is reported to the user — never silent.

## 2. Query Correctness
- [ ] Forward links return only semantic wikilinks (embeds excluded).
- [ ] Backlinks return all notes that contain `[[target]]` or `[[target|alias]]`.
- [ ] N-degree queries return exactly `depth` hops, not more.

## 3. Orphan Detection
- [ ] Orphans = notes with zero inbound AND zero outbound semantic links.
- [ ] Orphans are reported only, never auto-deleted or auto-linked.


## See Also

- [[acceptance-criteria-obsidian-bases-manager]]
- [[acceptance-criteria-obsidian-canvas-architect]]
- [[obsidian-graph-traversal]]
- [[procedural-fallback-tree-obsidian-graph-traversal]]
- [[acceptance-criteria-obsidian-init]]
- [[acceptance-criteria-obsidian-markdown-mastery]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-graph-traversal/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.125520+00:00
