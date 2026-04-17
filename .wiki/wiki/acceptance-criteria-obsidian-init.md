---
concept: acceptance-criteria-obsidian-init
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-init/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.127843+00:00
cluster: plugin-code
content_hash: 86b0b463d4737e66
---

# Acceptance Criteria: Obsidian Init

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Obsidian Init

## 1. Prerequisite Check
- [ ] Agent verifies Obsidian app, obsidian-cli, and ruamel.yaml before running init.
- [ ] Missing prerequisites are reported individually with install commands.

## 2. Vault Initialization
- [ ] `.obsidian/app.json` is created with default exclusion filters.
- [ ] `.gitignore` is updated to exclude `.obsidian/`.
- [ ] `--validate-only` makes NO filesystem changes.

## 3. Safety
- [ ] Agent does NOT initialize a directory with no `.md` files without explicit user confirmation.
- [ ] Init script is idempotent — re-running on an already-initialized vault does not corrupt config.


## See Also

- [[acceptance-criteria-os-init]]
- [[acceptance-criteria-hf-init]]
- [[acceptance-criteria-obsidian-bases-manager]]
- [[acceptance-criteria-obsidian-canvas-architect]]
- [[acceptance-criteria-obsidian-graph-traversal]]
- [[acceptance-criteria-obsidian-markdown-mastery]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-init/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.127843+00:00
