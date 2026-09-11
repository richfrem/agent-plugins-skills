# Skill Review Rubric & Alignment Invariants

This rubric establishes a 4-tier severity classification for auditing and aligning skills across the ecosystem.

## 4-Tier Severity Classification

| Tier | Name | Criteria & Violations | Resolution |
|---|---|---|---|
| **P0** | **Blocking** | Broken frontmatter, missing `SKILL.md`, invalid evals schema (missing `should_trigger`), real file script imposter (ADR-002/003 violation), invalid slug. | Hard gate. Must resolve before merge or deploy. |
| **P1** | **High** | `SKILL.md` exceeds 80 lines without progressive disclosure, missing `references/acceptance-criteria.md`, description > 1024 chars. | Must offload procedural/reference details to `references/`. |
| **P2** | **Medium** | Description exceeds 800 chars, first-person phrasing in description, missing `references/fallback-tree.md`, missing evals file. | Refactor description to active 3rd-person; wire fallback tree. |
| **P3** | **Low** | Cosmetic formatting inconsistencies, suggested eval prompt diversity improvements. | Optional refinement. |

## Progressive Disclosure & Context Efficiency

1. **Layer 1 Procedural Router**:
   - `SKILL.md` must remain lean (target <= 80 lines).
   - Serves as the high-level router and entry point with deterministic execution commands.
2. **Layer 2 Reference Specifications**:
   - Background tables, multi-environment matrices, API schemas, and architecture guides reside in `references/`.
   - The LLM reads reference files on-demand rather than loading them on every skill trigger.

## Knowledge vs Execution Separation

- **Execution**: Managed deterministically by Python scripts in `scripts/`.
- **Reasoning**: Managed by the LLM following instructions in `SKILL.md`.
- **Knowledge**: Stored in `references/` markdown and loaded as progressive disclosure context.
