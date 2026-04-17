---
concept: procedural-fallback-tree-obsidian-init
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-init/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.128064+00:00
cluster: action
content_hash: dd8a7d8d183375a5
---

# Procedural Fallback Tree: Obsidian Init

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Obsidian Init

## 1. Obsidian App Not Installed
If `ls /Applications/Obsidian.app` fails:
- **Action**: Report explicitly that the Obsidian desktop app is required. Provide the Homebrew install command. Do NOT proceed with vault init until the user confirms Obsidian is installed.

## 2. Target Directory Has No Markdown Files
If `../scripts/init_vault.py` reports zero `.md` files found:
- **Action**: Report the finding and ask the user to confirm they want to initialize an empty vault. Do NOT silently create `.obsidian/` in an unintended directory.

## 3. `.gitignore` Write Permission Denied
If updating `.gitignore` fails with `PermissionError`:
- **Action**: Report the permission failure. Print the lines that should be added manually. Do NOT skip the gitignore update silently — unexpectedly committed `.obsidian/` config causes conflicts.

## 4. `--validate-only` Shows Failures
If validation reports missing `.obsidian/` config but the user asked for validate-only:
- **Action**: Report findings clearly but make NO changes. If user then asks to fix, run a new session with the init command (without `--validate-only`).


## See Also

- [[procedural-fallback-tree-hf-init]]
- [[procedural-fallback-tree-obsidian-bases-manager]]
- [[procedural-fallback-tree-obsidian-canvas-architect]]
- [[procedural-fallback-tree-obsidian-graph-traversal]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-vault-crud]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-init/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.128064+00:00
