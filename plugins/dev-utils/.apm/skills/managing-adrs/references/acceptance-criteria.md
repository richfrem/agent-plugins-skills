# Acceptance Criteria: managing-adrs

## 1. Scaffolding
- [ ] `python3 scripts/adr_manager.py create "<Title>"` writes one new ADR from `assets/templates/adr-template.md` with the next free number.
- [ ] Creating an ADR never overwrites an existing record.

## 2. Numbering
- [ ] `python3 scripts/next_number.py --type adr` returns the next unused ADR number.
- [ ] From inside a git worktree, numbering resolves against that worktree's checkout (via `git rev-parse --show-toplevel`), not another checkout.

## 3. Querying
- [ ] `adr_manager.py list`, `get <NUMBER>` and `search "<KEYWORD>"` read records without modifying them.
- [ ] `get` on a missing number reports it clearly and exits non-zero.

## 4. Content
- [ ] Each ADR records context, decision, consequences and alternatives considered.
- [ ] Related decisions are cross-referenced by number (for example `ADR-003`).
