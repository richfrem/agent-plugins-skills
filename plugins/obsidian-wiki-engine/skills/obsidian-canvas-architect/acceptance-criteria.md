# Acceptance Criteria: Obsidian Canvas Architect

## 1. JSON Canvas Compliance
- [ ] All `.canvas` files conform to JSON Canvas Spec 1.0 (nodes + edges arrays).
- [ ] Node IDs are UUID-generated, never user-specified strings.
- [ ] All required fields are present before write (validated by schema check).

## 2. Atomic Writes
- [ ] All canvas writes route through `obsidian-vault-crud` atomic write protocol.
- [ ] No direct file writes — canvas_ops.py never bypasses vault_ops.py.

## 3. Error Handling
- [ ] Malformed JSON triggers a clean error report, never a crash.
- [ ] Edges referencing non-existent nodes are flagged before writing.
