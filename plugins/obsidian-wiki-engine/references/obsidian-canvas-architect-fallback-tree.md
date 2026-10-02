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
