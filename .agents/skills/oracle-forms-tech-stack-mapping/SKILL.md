---
name: oracle-forms-tech-stack-mapping
description: The Architect. Mandatory guide for mapping Oracle Forms elements to the Sandbox React/.NET architecture. Use when converting Forms to Modern Code.
---

# Oracle Forms Tech Stack Mapping (The Architect)

**The Architect** represents the authoritative decision-making logic for the Transitional Architecture. You must consult this skill before generating any React components or .NET APIs to ensure they align with the "Zero-Change DB", "Strict Mirroring", and "Pass-through Auth" policies.

## Document Authority Hierarchy

When documents conflict, follow this precedence order:

| Level | Document | Role |
|:---|:---|:---|
| **L1 (Law)** | [Migration Matrix](/plugins/legacy system/resources/architecture/transitory/Oracle_Forms_Migration_Matrix.md) — **detailed mapping tables** | What maps to what (authoritative per ADR-0035) |
| **L2 (Pattern)** | [Trigger Pipeline](/plugins/legacy system/resources/architecture/transitory/patterns/trigger_execution_pipeline.md), [Record Group Strategy](/plugins/legacy system/resources/architecture/transitory/patterns/record_group_strategy.md), [Element Mapper IR](/plugins/legacy system/resources/architecture/transitory/element-mapper-design.md) | How to implement specific element types |
| **L3 (Policy)** | [Transitional Architecture](/plugins/legacy system/resources/architecture/transitory/transitional_architecture_details.md), `plugins/legacy system/resources/rules/03_TECHNICAL/legacy_sql_and_plsql_policy.md` | Constraints (Zero-Change DB, Strict Mirroring, Pass-through Auth) |
| **L4 (Reference)** | [Design Reviews](/plugins/legacy system/resources/architecture/transitory/reviews/), [Refined IR Models](/plugins/legacy system/resources/architecture/transitory/reviews/refined_ir_models.md) | Decision rationale and history |

> **Important**: The Migration Matrix contains both a detailed mapping table (L1, authoritative) and a 43-processor quick-reference summary. When they differ, the **detailed table takes precedence**.

## When to use this skill

- **Mapping**: "How do I convert a Block to React?"
- **Patterns**: "What is the pattern for an LOV?" or "How do triggers work?"
- **Configuration**: "Where should I put the `menuConfig`?"
- **Backend**: "Map this trigger to .NET."
- **Policy**: Any question involving database changes, PL/SQL mirroring, or security.

## How to use it (The Decision Tree)

Follow this decision tree to determine the correct mapping strategy:

### 1. Identify the Element Type & Complexity
Classify the element using the **Complexity Levels**:
*   **Level 1 (Attributes Only)**: Alert, Trigger, Window, Canvas.
*   **Level 2 (Simple Containers)**: Item, LOV, Menu.
*   **Level 3 (Intermediate)**: Block, RecordGroup.
*   **Level 4 (Modules)**: FormModule, MenuModule, ObjectLibrary.

### 2. Consult the Source of Truth (The Matrix)
**Goal**: Find the specific mapping rule.
*   **Read**: `plugins/legacy system/resources/architecture/transitory/Oracle_Forms_Migration_Matrix.md`
*   **Use**: The **detailed mapping tables** at the top of the document (not just the 43-processor summary).
*   **For Triggers specifically**: Also read [Trigger Execution Pipeline](/plugins/legacy system/resources/architecture/transitory/patterns/trigger_execution_pipeline.md) — covers event lifecycle ordering, `RAISE FORM_TRIGGER_FAILURE` handling, `ExecuteHierarchy`, and Forms built-in mapping.
*   **For RecordGroups specifically**: Also read [Record Group Strategy](/plugins/legacy system/resources/architecture/transitory/patterns/record_group_strategy.md) — covers Type A/B/C/D classification and hidden WHERE clause analysis.
*   **For GLOBAL/SYSTEM variables**: See the "GLOBAL and SYSTEM Variable Mapping" section in the Migration Matrix.
*   **For inter-form navigation** (`CALL_FORM`, `OPEN_FORM`, `NEW_FORM`): See the "Inter-Form Navigation Strategy" section in the Migration Matrix.

### 3. Verify Architectural Constraints
**Goal**: Ensure compliance with "Zero-Change" and "Strict Mirroring" rules.
*   **Read**: `plugins/legacy system/resources/architecture/transitory/transitional_architecture_details.md`
*   **Read**: `plugins/legacy system/resources/rules/03_TECHNICAL/legacy_sql_and_plsql_policy.md`
*   **Check**:
    *   **Zero-Change DB**: Are you trying to add a table? **STOP**. Use ODP.NET wrapper.
    *   **Strict Mirroring**: Are you rewriting a PL/SQL package in C#? **STOP**. Call the package procedure directly using `LegacySharedService`.
    *   **Pass-through Auth**: Are you building a login page? **STOP**. Use the existing pattern.
    *   **Security Model**: During Phase 1, the Oracle DB enforces authorization (VPD/Roles). The .NET API is pass-through. `MenuItemRole` controls **UI visibility only**, not backend enforcement. See Section 5C of the transitional architecture doc.

### 4. Implement using Frontend Patterns
**Goal**: Structure the React code correctly.
*   **Read**: `plugins/legacy system/resources/architecture/transitory/element-mapper-design.md`
*   **Follow**:
    *   **Direct API Strategy**: React calls .NET API directly (No Node.js BFF).
    *   **IR Model**: Use the `ModernizedFormElement` structure.
    *   **Zod Validation**: Implement client-side validation logic.
    *   **UI Library**: `@bcgov/design-tokens` with Material UI components. TanStack Table for grids. React Hook Form + Zod for form state.

## Best Practices

### The "Electric Fence" (Strict Constraints)
1.  **Immutable Database**: Never propose SQL DDL (CREATE/ALTER) as part of a conversion task.
2.  **No Logic Rewrites**: Do not rewrite complex PL/SQL in C# unless it is purely UI manipulation. Wrap it in `LegacySharedService`.
3.  **PlsqlToDotnet Scaffold**: `tools/codify/converter/plsql_to_dotnet.py` generates **starting-point** boilerplate for `LegacySharedService`. **Review and correct the output** — it has known limitations:
    *   PascalCase conversion is naive (concatenates before casing)
    *   Type map is incomplete (missing CLOB, BLOB, BOOLEAN, TIMESTAMP, decimal NUMBER)
    *   `NUMBER` defaults to `int` — verify if `decimal` is needed (financial data)
    *   Parameter modes (IN/OUT/IN OUT) are not parsed
    *   FUNCTION return types are not captured
    *   PL/SQL control flow (IF/LOOP/EXCEPTION) is dropped — only cursors are extracted
4.  **Strict File Paths**: Always output to `sandbox/`. Never touch `legacy-system/` unless reading.

### The "Golden Path" (Recommended Workflow)
1.  **Read Context**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle --target [ID]`
2.  **Plan**: Create `spec.md` listing the element types involved and their mapping targets.
3.  **Map**: Use the detailed Migration Matrix tables to define the React/.NET split.
4.  **Generate**: Write code to `sandbox/src/components/forms/[ID]/`.