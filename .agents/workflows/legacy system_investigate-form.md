---
description: Complete reusable analysis module for Oracle Forms. Handles context initialization...
---

---
description: Complete reusable analysis module for Oracle Forms. Handles context initialization...
inputs: [FormID]
tier: 2
# /legacy-system-oracle-forms_investigate-form

**Purpose:** Complete reusable analysis module for Oracle Forms. Handles context initialization, recursive discovery, and multi-pass mining. Called by `/legacy-system-oracle-forms_codify-form` (documentation) and `/legacy-system-oracle-forms_modernize-form` (React code generation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
/legacy-system-oracle-forms_investigate-form [FormID]
```
*Note:* This initializes the manifest and builds the initial `[FormID]_context.md` bundle.

### Step 2: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[FormID]_context.md
view_file legacy-system/oracle-forms-overviews/forms/[FormID]-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (XML/MD)?
2. Does it have RLM summaries for key dependencies?
3. Does it have dependency graph entries?

## Phase 2: Recursive Verification Loop (The "Context Spiral")

**Diagram:** ../docs/diagrams/workflows/form-discovery.mmd
**Objective:** Expand context by engaging as a **Recursive Language Model (RLM)**—picking initial context, bundling it with the `bundler-plugin`, and looping through adding more context incrementally and recursively, pull only the context required for the job.

> **⚠️ CRITICAL: This is an ITERATIVE LOOP, not a one-shot process.**
> Repeat Steps until the context is complete.
>
> **Protocol:** See [context-spiral-protocol.md](../../coding-conventions/docs/context-spiral-protocol.md) for detailed definitions of Levels 1-4.

### Stop Condition & Iteration Limit
- **Max Iterations:** 3 Loop Cycles.
- **Error:** If context is still incomplete after 3 cycles, STOP and notify the user. Do not loop infinitely.

```
┌─────────────────────────────────────────────────────────┐
│              RECURSIVE LANGUAGE MODEL (RLM)             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Review  │───►│ Add File │───►│ Rebundle │───┐       │
│  │  Bundle  │◄───┴──────────┴────┴──────────┘   │       │
│  └────┬─────┘                                   │       │
│       │ Context Complete?                       │       │
│       ▼                                         │       │
│   [YES: Proceed to Mining]    [NO: Loop]────────┘       │
└─────────────────────────────────────────────────────────┘
```

### Level 1: Forms (CALL_FORM)
1. **Analyze:** Check `[FormID]_context.md` for `CALL_FORM` or `OPEN_FORM` targets.
2. **Action:** If missing from bundle:
   - **Command:** `/context-bundler_add --path relative/path/to/fmb`
   - **Rebundle:** `/context-bundler_bundle`

### Level 2: Libraries (PLL)
1. **Analyze:** Check for `AttachedLibrary` (`.pll`).
2. **Action:** Ensure the bundle contains the library source or RLM summary.
   - **Command:** `/context-bundler_add --path .../pll/[LIB].txt`
   - **Rebundle:** `/context-bundler_bundle`

### Level 3: DB Objects (Pkgs/Procs/Funcs/Views)
1. **Analyze:** Trace triggers for key `Database Packages`, `Procedures`, `Functions`, and `Views`.
2. **Action:** Add referenced database artifacts.
   - **Command:** `/context-bundler_add --path .../Tables/[TABLE].sql`
   - **Rebundle:** `/context-bundler_bundle`

*Stop Condition:* Proceed ONLY when `[FormID]_context.md` contains key elements.
See [Completeness Checklist](../../coding-conventions/docs/context-spiral-protocol.md#3-completeness-checklist-stop-condition) in protocol.

### Context Completeness Checkpoint
Before moving to Phase 3, you MUST run:
```bash
# Check if key dependencies are present in the bundle
grep -E "attachedLibrary|call_form|menuModule" temp/context-bundles/[FormID]_context.md
```
If output is empty but you know dependencies exist, **FAIL THE TASK** and debug the `.agent/skills/context-bundler/scripts/manifest_manager.py bundle` step.

## Phase 3: Multi-Pass Mining (The Detective)

### What It Extracts

| Category | Extraction Target | Modern Mapping |
|----------|------------------|----------------|
| **Blocks** | DMLDataName, Relations, ORDER BY | API Endpoints, React Query dependencies |
| **Triggers** | WHEN-*, KEY-*, PRE/POST | useEffect, event handlers, Zod validation |
| **UI Layout** | Canvases, Windows, TabPages | React components, Tabs, Modals |
| **Navigation** | CALL_FORM, OPEN_FORM, NEW_FORM | React Router, Modal dialogs |
| **Security** | GLOBAL.*, Role checks, SET_ITEM_PROPERTY | Auth guards, RBAC hooks |

### Pass 1: Blocks & Data Model
**Focus:** Database structure, master-detail relationships
```bash
/legacy-system-oracle-forms_investigate-form [FormID] (XML Pass)
```
**Extracts:**
- `DMLDataName` → API Endpoint (`/api/t/[TableName]`)
- `Relations` → React Query dependencies
- `ORDER BY` → Default Grid Sort State

### Pass 2: Triggers & Logic
**Focus:** Event-driven logic (WHEN-*, KEY-*)
```bash
/legacy-system-database_investigate-code-search --target [FormID] --query "WHEN-|KEY-|PRE-|POST-"
```
**Extracts:**
- `WHEN-NEW-FORM-INSTANCE` → `useEffect` (onMount)
- `WHEN-VALIDATE-ITEM` → `useForm` validation rules (Zod schema)
- `KEY-DELREC` → `handleDelete` with Confirmation Modal

### Pass 3: UI Layout
**Focus:** Canvases and Windows
```bash
/legacy-system-database_investigate-code-search --target [FormID] --query "Canvas|Window|TabPage|SHOW_VIEW"
```
*(Extracts: Tab Canvas, Stacked Canvas, Modals)*

### Pass 4: Navigation
**Focus:** Inter-form calls
```bash
/legacy-system-database_investigate-code-search --target [FormID] --query "CALL_FORM|OPEN_FORM|NEW_FORM"
```
*(Extracts: CALL_FORM, NEW_FORM mappings)*

### Pass 5: Security
**Focus:** Role checks and Global State
```bash
/legacy-system-database_investigate-code-search --target [FormID] --query "GLOBAL\\.[A-Z_]+"
/legacy-system-roles_investigate-form-roles [FormID]
```
**Extracts:**
- `IF :GLOBAL.ROLE = 'Y'` → `if (hasRole(Roles.ADMIN))`
- `SET_ITEM_PROPERTY(..., VISIBLE, FALSE)` → `{canView && <Button />}`

## Phase 4: Dependency & Lineage Analysis

### Step 6a: System-Wide Dependency & Intent
```bash
/dependency-analysis_retrieve-dependency-graph [FormID] --downstream
```
> **Rule:** For context analysis, focus on **Downstream** (Processing Logic). Upstream (Callers) is for Impact Analysis only.

### Step 6b: Application Discovery (Parent Modules)
```bash
/legacy-system-oracle-forms_investigate-lineage [FormID]
```
### Step 7: Lineage Check (Dead Code Analysis)
```bash
/legacy-system-oracle-forms_investigate-lineage [FormID]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

## Phase 5: Business Rule & Security Discovery

### Step 8: Search Existing Rules (MANDATORY)
Before flagging ANY new business rule, search first to prevent duplicates:
```bash
/legacy-system-business-rules_investigate-business-rule "keyword"
```

### Step 9: Flag Rule Candidates (If Found)
If critical logic discovered that isn't documented:
```bash
/legacy-system-business-rules_codify-business-rule --source [FormID] --description "Title"
```

### Step 10: Security Verification
```bash
/legacy-system-roles_investigate-role [RoleName]
```
- Verify all discovered roles against `roles_inventory.json`
- Identify Active vs Legacy/Deprecated roles

### Step 11: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source XML/Markdown
- [ ] All CALL_FORM targets
- [ ] Attached Libraries (PLL)
- [ ] Menu Module reference
- [ ] Key Database Packages
- [ ] Business Rule candidates flagged
- [ ] Security roles verified

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[FormID]_context_bundle.md`)
- Console output with extracted patterns
- Rule candidates (registered via CLI)
- Security verification results

**Called By:**
- `/codify-form` → Uses output to fill documentation template
- `/modernize-form` → Uses output to generate React code

**See Also:**
- `plugin architecture` - Discover valid tools for specific tasks.
- `dependencies.py --target [FormID] --deep --json` - Get dependencies with file paths
- `dependencies.py --target [FormID] --applications` - Trace to parent applications
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ total)

// turbo-all