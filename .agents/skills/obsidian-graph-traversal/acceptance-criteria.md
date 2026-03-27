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
