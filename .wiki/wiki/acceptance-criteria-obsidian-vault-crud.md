---
concept: acceptance-criteria-obsidian-vault-crud
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-vault-crud/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.132050+00:00
cluster: write
content_hash: 31b4fe6800f020f9
---

# Acceptance Criteria: Obsidian Vault CRUD

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Obsidian Vault CRUD

## 1. Atomic Write
- [ ] All file writes stage to `<target>.agent-tmp` first, then rename atomically via `os.rename()`.
- [ ] If any step fails, the `.agent-tmp` file is cleaned up and the error is reported.

## 2. Locking
- [ ] `.agent-lock` is created at vault root before any write batch.
- [ ] `.agent-lock` is removed after the write batch completes.
- [ ] If `.agent-lock` already exists, the agent reports and waits rather than overriding.

## 3. Concurrent Edit Detection
- [ ] `st_mtime` is captured before reading a file.
- [ ] `st_mtime` is checked again before writing. If changed, the write is aborted.

## 4. Frontmatter Fidelity
- [ ] `ruamel.yaml` is used exclusively — never `PyYAML`.
- [ ] YAML comments, indentation, and array styles are preserved after a round-trip.


## See Also

- [[acceptance-criteria-obsidian-bases-manager]]
- [[acceptance-criteria-obsidian-canvas-architect]]
- [[acceptance-criteria-obsidian-graph-traversal]]
- [[acceptance-criteria-obsidian-init]]
- [[acceptance-criteria-obsidian-markdown-mastery]]
- [[obsidian-vault-crud]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-vault-crud/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.132050+00:00
