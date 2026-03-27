# oracle-forms-tech-stack-mapping

The Architect. Mandatory reference guide for mapping Oracle Forms elements to the Sandbox React/.NET architecture. Consult this skill before generating any React components or .NET APIs.

## When to Use

- Mapping an Oracle Forms element to a React/TypeScript equivalent
- Implementing triggers, LOVs, blocks, or record groups in the modern stack
- Verifying compliance with Zero-Change DB, Strict Mirroring, or Pass-through Auth policies
- Any question about database changes, PL/SQL mirroring, or security during modernization

## Document Authority Hierarchy

| Level | Document | Role |
|---|---|---|
| L1 (Law) | `Oracle_Forms_Migration_Matrix.md` | Authoritative element-to-element mapping tables |
| L2 (Pattern) | `trigger_execution_pipeline.md`, `record_group_strategy.md`, `element-mapper-design.md` | Implementation patterns for specific element types |
| L3 (Policy) | `transitional_architecture_details.md`, `legacy_sql_and_plsql_policy.md` | Constraints: Zero-Change DB, Strict Mirroring, Pass-through Auth |
| L4 (Reference) | Design reviews, refined IR models | Decision rationale and history |

> When the Migration Matrix detailed tables conflict with its 43-processor summary, the detailed tables take precedence.

## Core Constraints ("Electric Fence")

1. **Zero-Change DB** — Never propose SQL DDL (CREATE/ALTER). Use ODP.NET wrappers.
2. **No Logic Rewrites** — Do not rewrite PL/SQL in C#. Wrap it in `LegacySharedService`.
3. **Strict File Paths** — Always output to `sandbox/`. Never write to `legacy-system/`.
4. **Pass-through Auth** — Use the existing auth pattern; do not build a new login flow.

## Frontend Stack

- UI: `@bcgov/design-tokens` + Material UI
- Tables: TanStack Table
- Forms: React Hook Form + Zod
- API: React calls .NET directly (no Node.js BFF)
