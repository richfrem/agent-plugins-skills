---
description: Complete reusable analysis module for Oracle Reports. Handles context initializati...
---

---
description: Complete reusable analysis module for Oracle Reports. Handles context initializati...
inputs: [ReportID]
tier: 2
# /investigate-report

**Purpose:** Complete reusable analysis module for Oracle Reports. Handles context initialization, query extraction, and dependency tracing. Called by `/codify-report` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
/legacy-system-oracle-forms_investigate-report [ReportID]
```
*Note:* This initializes the manifest and builds the initial `[ReportID]_context.md` bundle.

### Step 2: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[ReportID]_context_bundle.md
view_file legacy-system/oracle-reports-overviews/[ReportID]-Report-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (XML)?
2. Does it have RLM summaries for called packages?

## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Diagram:** `../skills/legacy-system-oracle-forms/references/diagrams/workflows/report-discovery.mmd`
**Objective:** Expand context by tracing data dependencies (Tables, Packages).

> **⚠️ CRITICAL: This is an ITERATIVE LOOP, not a one-shot process.**
> Repeat Steps until the context is complete.
>
> **Protocol:** See [context-spiral-protocol.md](../../docs/standards/context-spiral-protocol.md) for definitions.

```
┌─────────────────────────────────────────────────────────┐
│                    RECURSION LOOP                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Review  │───►│ Add File │───►│ Rebundle │───┐       │
│  │  Bundle  │◄───┴──────────┴────┴──────────┘   │       │
│  └────┬─────┘                                   │       │
│       │ Context Complete?                       │       │
│       ▼                                         │       │
│   [YES: Proceed to Mining]    [NO: Loop]────────┘       │
└─────────────────────────────────────────────────────────┘
### Level 1: Core Content (The Source)
- Verify `[ReportID]_context_bundle.md` contains the full Report XML.

### Level 2: Dependencies (Tables & Packages)
1. **Trace:** Run dependency CLI:
   ```bash
   /dependency-analysis_retrieve-dependency-graph [ReportID] --downstream
   ```
2. **Action:** Identify key tables/packages used in queries.
   - **Command:** `/context-bundler_add --path ...`
   - **Rebundle:** `/context-bundler_bundle`

*Stop Condition:* Proceed ONLY when context contains Source and Data Dependencies.

## Phase 3: Mining (The Detective)

### Step 3: Run Report Miner
```bash
/legacy-system-oracle-forms_investigate-report [ReportID] (Mining Pass)
```
*Extracts: Queries, Data Model, Triggers, Parameters.*

### What It Extracts

| Category | Extraction Target | Modern Mapping |
|----------|------------------|----------------|
| **Queries** | SQL select statements | API Endpoints |
| **Data Model** | Groups, Links, Columns | DTOs / Domain Models |
| **Parameters** | User inputs (lexical/bind) | Search Filters |
| **Triggers** | Before/After Report logic | Business Logic / Validation |
| **Layout** | Frames, Fields, Boilerplate | PDF Generation / React Components |

## Phase 4: Dependency & Lineage Analysis

### Step 4: System-Wide Dependency Check
```bash
/dependency-analysis_retrieve-dependency-graph [ReportID] --both
```

### Step 5: Application Discovery (Parent Modules)
```bash
/legacy-system-oracle-forms_investigate-lineage [ReportID]
```
*Identifies which applications/forms call this report.*

### Step 6: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [ReportID]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

### Step 7: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source Code (XML)
- [ ] List of Queries/Data Model
- [ ] Referenced Tables/Packages
- [ ] Calling Forms (Upstream identified in Step 4)
- [ ] Application context identified

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[ReportID]_context.md`)
- Miner JSON output with report structure
- Extracted SQL queries

**Called By:**
- `/codify-report` → Uses output to fill documentation template

**See Also:**
- `dependencies.py --target [ReportID] --deep --json` - Get dependencies with file paths
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ relationships)

// turbo-all