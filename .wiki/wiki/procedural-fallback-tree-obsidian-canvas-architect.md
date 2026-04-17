---
concept: procedural-fallback-tree-obsidian-canvas-architect
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-canvas-architect/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.123703+00:00
cluster: node
content_hash: 3589bdb9b50c0167
---

# Procedural Fallback Tree: Obsidian Canvas Architect

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Obsidian Canvas Architect

## 1. Malformed Existing Canvas JSON
If `canvas_ops.py read` or any add operation detects invalid JSON:
- **Action**: Report the error with the file path. Do NOT attempt auto-repair. Ask the user to restore from backup or recreate. Never write to a canvas with a broken JSON structure.

## 2. Duplicate Node ID
If a node ID collision is detected (rare, UUID collision):
- **Action**: Regenerate a new UUID and retry once. If collision persists after retry, report to the user. Do NOT silently overwrite the existing node.

## 3. Edge References Non-Existent Node
If an edge's `fromNode` or `toNode` ID does not exist in the canvas:
- **Action**: Report the dangling edge reference before writing. Ask user to confirm node IDs. Do NOT write an edge pointing to a non-existent node.


## See Also

- [[procedural-fallback-tree-obsidian-bases-manager]]
- [[procedural-fallback-tree-obsidian-graph-traversal]]
- [[procedural-fallback-tree-obsidian-init]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-vault-crud]]
- [[procedural-fallback-tree-obsidian-bases-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-canvas-architect/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.123703+00:00
