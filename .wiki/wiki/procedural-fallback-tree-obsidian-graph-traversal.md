---
concept: procedural-fallback-tree-obsidian-graph-traversal
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-graph-traversal/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.125737+00:00
cluster: index
content_hash: bd93c1c32e027b4a
---

# Procedural Fallback Tree: Obsidian Graph Traversal

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[procedural-fallback-tree-obsidian-bases-manager]]
- [[procedural-fallback-tree-obsidian-canvas-architect]]
- [[procedural-fallback-tree-obsidian-init]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-vault-crud]]
- [[procedural-fallback-tree-obsidian-bases-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-graph-traversal/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.125737+00:00
