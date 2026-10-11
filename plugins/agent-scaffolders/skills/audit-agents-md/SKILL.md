---
name: audit-agents-md
description: Audits root instruction files (AGENTS.md, CLAUDE.md) for size budgets, timelessness, progressive disclosure, and inline invariants. Use when reviewing, auditing, or trimming root instruction files.
plugin: agent-scaffolders
category: verification
---

# Audit AGENTS.md / CLAUDE.md

Deterministic and judgment audit for repository root instruction files to prevent context bloat, enforce timeless invariants, and ensure progressive disclosure.

## Quick Start

```bash
# Audit repository AGENTS.md
python3 scripts/audit_agents_md.py AGENTS.md

# Scan all instruction files with strict mode
python3 scripts/audit_agents_md.py . --all --strict
```

## Tier 1: Deterministic Invariants

Evaluates target files against `references/agents-md-contract.md`:
1. **Transitive Eager Budget**: Target <= 100 lines (WARN > 120 lines, FAIL > 200 lines). Recursively resolves eager `@imports`.
2. **Platform Bridge**: Verifies `CLAUDE.md` is a thin bridge (<= 5 lines) pointing to `AGENTS.md`.
3. **Timelessness**: Zero calendar dates (`YYYY-MM-DD`). Invariants must be timeless.
4. **Environment Agnosticism**: Zero absolute machine paths (`/Users/`, `/home/`, `C:\`).
5. **Progressive Disclosure**:
   - No ASCII directory trees (point to `architecture.md`).
   - No inlined pitfall catalogs (point to `docs/architecture/known-pitfalls.md` or `references/`).
   - No redundant Key Files or Tool Name Mapping tables.
6. **Invariants vs. Procedures**:
   - MUST/NEVER/ALWAYS/DO NOT invariants must be stated inline (not deferred entirely to a link).
   - Links point to `.agent/rules/<rule>.md` for rationale and examples.

## Tier 2: Judgment Review (Advisory)

When conducting qualitative review:
1. Apply the **Pruning Test**: "Would removing this line cause an AI agent to make mistakes?" If not, prune it.
2. Check for **Procedures Masquerading as Rules**: Multi-step workflows (>3 steps) should be migrated to specialized skills.
3. Check for **Overuse of Emphasis**: Avoid excessive ALL-CAPS or screaming warnings that dilute signal.

## References

- [Contract](references/agents-md-contract.md)
