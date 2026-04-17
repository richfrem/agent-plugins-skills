---
concept: procedural-fallback-tree-obsidian-bases-manager
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-bases-manager/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.121631+00:00
cluster: yaml
content_hash: ce1134cc7e01deb3
---

# Procedural Fallback Tree: Obsidian Bases Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Obsidian Bases Manager

## 1. Malformed YAML in Base File
If `../scripts/bases_ops.py` reports a YAML parse error:
- **Action**: Report the error with line number. Do NOT attempt auto-repair. Ask user to restore from backup. Never write to a Base file with corrupt YAML.

## 2. Row Index Out of Bounds
If `update-cell` is called with a row index that doesn't exist:
- **Action**: Run `./bases_ops.py read` to show current row count. Report the valid index range. Do NOT silently create a new row at the requested index.

## 3. ruamel.yaml Import Fails
If `import ruamel.yaml` raises `ImportError`:
- **Action**: Do NOT fall back to standard yaml or json. Report the missing dependency: `pip install ruamel.yaml`. Halt all Base file operations until resolved.


## See Also

- [[procedural-fallback-tree-obsidian-canvas-architect]]
- [[procedural-fallback-tree-obsidian-graph-traversal]]
- [[procedural-fallback-tree-obsidian-init]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-vault-crud]]
- [[procedural-fallback-tree-obsidian-canvas-architect]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-bases-manager/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.121631+00:00
