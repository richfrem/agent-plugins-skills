---
concept: procedural-fallback-tree-obsidian-markdown-mastery
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-markdown-mastery/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.130166+00:00
cluster: type
content_hash: eb6f4c323b0fc731
---

# Procedural Fallback Tree: Obsidian Markdown Mastery

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Obsidian Markdown Mastery

## 1. parser.py Not Found
If `parser.py` cannot be located at `./parser.py`:
- **Action**: Do NOT write ad-hoc regex to parse markdown. Report that the parser module is missing. Ask the user to verify the plugin is installed correctly.

## 2. OBSIDIAN_VAULT_PATH Not Set
If the `OBSIDIAN_VAULT_PATH` environment variable is not set and a tool needs the vault root:
- **Action**: Default to the project root (current working directory) as per the skill spec. Log a warning. Do NOT fail — this is documented fallback behavior.

## 3. Unsupported Callout Type
If the user requests a callout type not in the supported list (info, warning, error, success, note):
- **Action**: Report the unsupported type. Map to the closest supported type and ask the user to confirm before injecting the callout. Do NOT silently use an arbitrary type.


## See Also

- [[procedural-fallback-tree-context-bundler-markdown]]
- [[procedural-fallback-tree-markdown-to-ms-word-conversion]]
- [[procedural-fallback-tree-obsidian-bases-manager]]
- [[procedural-fallback-tree-obsidian-canvas-architect]]
- [[procedural-fallback-tree-obsidian-graph-traversal]]
- [[procedural-fallback-tree-obsidian-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-markdown-mastery/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.130166+00:00
