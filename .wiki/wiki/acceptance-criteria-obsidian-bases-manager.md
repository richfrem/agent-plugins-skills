---
concept: acceptance-criteria-obsidian-bases-manager
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-bases-manager/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.121422+00:00
cluster: yaml
content_hash: 960cf57cd10ba635
---

# Acceptance Criteria: Obsidian Bases Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Obsidian Bases Manager

## 1. View Config Preservation
- [ ] Append-row and update-cell operations NEVER modify columns, filters, sorts, or formulas.
- [ ] Only the data section of the `.base` file changes after a write operation.

## 2. YAML Fidelity
- [ ] `ruamel.yaml` is used exclusively — never `PyYAML` or `json`.
- [ ] YAML comments and formatting are preserved after a round-trip read/write.

## 3. Error Handling
- [ ] Malformed YAML triggers a clean error with line number — no crash, no data loss.
- [ ] Out-of-bounds row index reports valid range rather than silently creating extra rows.


## See Also

- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[obsidian-bases-manager]]
- [[procedural-fallback-tree-obsidian-bases-manager]]
- [[acceptance-criteria-obsidian-canvas-architect]]
- [[acceptance-criteria-obsidian-graph-traversal]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-bases-manager/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.121422+00:00
