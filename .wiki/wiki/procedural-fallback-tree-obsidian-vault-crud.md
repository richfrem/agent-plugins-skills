---
concept: procedural-fallback-tree-obsidian-vault-crud
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-vault-crud/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.132273+00:00
cluster: write
content_hash: 50df5c75ef6e64c2
---

# Procedural Fallback Tree: Obsidian Vault CRUD

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Obsidian Vault CRUD

## 1. Lock File Present
If `.agent-lock` exists at vault root when starting a write operation:
- **Action**: Do NOT override the lock. Report it to the user, showing the lock file path and creation time. Wait for user confirmation before retrying. Never auto-delete the lock.

## 2. Atomic Write Failed (tmp not renamed)
If `os.rename()` fails after writing to `.agent-tmp`:
- **Action**: Clean up the `.agent-tmp` file. Report the failure with the OS error. Do NOT leave the `.agent-tmp` file in place. Do NOT attempt the write again without user confirmation.

## 3. Concurrent Edit Detected (mtime changed)
If `st_mtime` changed between read and intended write:
- **Action**: ABORT the write immediately. Report which file changed and ask the user to re-read the current content and confirm the intended change. Never proceed with a stale write.

## 4. ruamel.yaml Import Fails
If `import ruamel.yaml` raises `ImportError`:
- **Action**: Do NOT fall back to `PyYAML`. Report the missing dependency and provide the install command: `pip install ruamel.yaml`. Halt all CRUD operations until resolved.


## See Also

- [[procedural-fallback-tree-obsidian-bases-manager]]
- [[procedural-fallback-tree-obsidian-canvas-architect]]
- [[procedural-fallback-tree-obsidian-graph-traversal]]
- [[procedural-fallback-tree-obsidian-init]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-bases-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-vault-crud/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.132273+00:00
