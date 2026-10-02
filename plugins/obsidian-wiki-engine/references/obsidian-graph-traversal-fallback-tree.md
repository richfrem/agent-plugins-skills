# Procedural Fallback Tree: Obsidian Graph Traversal

## 1. Graph Index Missing or Stale
If `.graph-index.json` is absent or any file's `mtime` is newer than the index:
- **Action**: Run `graph_ops.py build` before any query. Never query a stale index and present results as current. Always report if a rebuild was performed.

## 2. Note Not Found in Index
If a forward-link or backlink query returns no results:
- **Action**: Verify the note name matches exactly (case-sensitive on macOS/Linux). Report "Note not found in index" and suggest rebuilding. Do NOT assume the note has zero connections — it may be a staleness issue.

## 3. Vault Root Contains No Markdown Files
If `graph_ops.py build` finds no `.md` files:
- **Action**: Report that the vault appears to be empty. Do NOT write an empty `.graph-index.json`. Ask user to verify the `--vault-root` path is correct.
