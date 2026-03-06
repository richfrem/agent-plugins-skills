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
