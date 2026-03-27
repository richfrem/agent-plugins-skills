---
description: Complete reusable analysis module for Oracle Database Functions. Handles context initialization, recursive discovery, and analysis.
inputs: [FunctionName]
tier: 2
---

# /investigate-db-function

**Purpose:** Complete reusable analysis module for Oracle Database Functions. Handles context initialization, recursive discovery, and analysis. Called by `/codify-db-function` (documentation).


## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [FunctionName] --type function
```
*Action:* Resets manifest, loads base Function manifest, populates dependencies.
*Output:* `temp/context-bundles/[FunctionName]_context.md` (Generated Bundle)

### Step 2: Locate Function Source
```bash
find_by_name --pattern "*[FunctionName]*.sql" --directory legacy-system/oracle-database/Functions
```
*Identify the target function file path.*

### Step 3: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[FunctionName]_context.md
view_file legacy-system/oracle-db-overviews/functions/[FunctionName]-Function-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (SQL)?
2. Does it have parameter/return type information?

## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Diagram:** `../skills/legacy-system-database/references/diagrams/workflows/db-function-discovery.mmd`
**Objective:** Expand context by tracing dependencies downstream.

> **⚠️ CRITICAL: This is an ITERATIVE LOOP, not a one-shot process.**
> Repeat Steps until the context is complete.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECURSION LOOP                                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                   │
│  │  Review  │───►│ Add File │───►│ Rebundle │───┐               │
│  │  Bundle  │◄───┴──────────┴────┴──────────┘   │               │
│  └────┬─────┘                                   │               │
│       │ Context Complete?                       │               │
│       ▼                                         │               │
│   [YES: Proceed to Mining]    [NO: Loop]────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

### Level 1: Core Content (The Source)
- Verify `[FunctionName]_context.md` contains the full function SQL source.

### Level 2: Downstream Dependencies (Tables/Views Called)
1. **Trace:** Run dependency CLI:
   ```bash
   python scripts/dependencies.py --target [FunctionName] --deep --direction downstream --json
   ```
2. **Action:** Identify tables, views, or other objects the function calls.
   - **Command:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path ...`
   - **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`
   - **Repeat** if more dependencies discovered.

### Level 3: Helper Functions/Packages
1. **Trace:** Check for calls to other functions or packages:
   ```bash
   python scripts/search_plsql.py --target [FunctionName] --pattern "PACKAGE|PROCEDURE|FUNCTION"
   ```
2. **Action:** Add related objects to manifest if critical.

*Stop Condition:* Proceed ONLY when context contains Source, Tables/Views, and key Package dependencies.

## Phase 3: Mining (The Detective)

### Step 4: Extract Function Signature
From the source, identify:
- **Parameters**: Name, Type, IN/OUT mode
- **Return Type**: Data type returned
- **Purpose**: From comments or naming conventions

### Step 5: Run DB Miner
```bash
python scripts/db_miner.py --target [FunctionName]
```
*Extracts: Parameter list, return type, table references, error handling.*

### What It Extracts

| Category | Extraction Target | Modern Mapping |
|----------|------------------|----------------|
| **Signature** | Parameters, Return Type | API endpoint signature |
| **Tables** | SELECT/INSERT/UPDATE targets | Data layer dependencies |
| **Validation** | RAISE_APPLICATION_ERROR | Business rules |
| **Complexity** | Lines, branches | Refactoring difficulty |

### Step 6: Search for Business Rules
```bash
python scripts/search_plsql.py --target [FunctionName] --pattern "RAISE_APPLICATION_ERROR|IF.*THEN"
```
*Identifies validation logic and error conditions.*

## Phase 4: Dependency & Lineage Analysis

### Step 7: System-Wide Dependency Check
```bash
python scripts/dependencies.py --target [FunctionName] --deep --direction both
```

### Step 8: Application Discovery (Parent Modules)
```bash
python scripts/generate_applications_inventory.py --target [FunctionName]
```
*Identifies which applications/forms use this function.*

### Step 9: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [FunctionName]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

### Step 10: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source Code (SQL)
- [ ] Function signature (parameters, return type)
- [ ] Downstream dependencies (tables, views)
- [ ] Upstream callers identified
- [ ] Application context identified
- [ ] Business rule candidates flagged

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[FunctionName]_context.md`)
- Console output with logic flow and patterns
- Validation rule candidates
- Security pattern documentation
- **Code Generator Handoff**: When generating migration scripts or test harnesses based on this analysis, the agent MUST format the output using the "Modular Building Blocks" architecture (separating convenience CLI wrappers from core functional Python/SQL APIs).
**Called By:**
- `/codify-db-function` → Uses output to fill documentation template

**See Also:**
- `dependencies.py --target [FunctionName] --deep --json` - Get dependencies with file paths
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ total)
- `/investigate-db-procedure` - Similar workflow for procedures
- `/investigate-db-package` - For package-contained functions

// turbo-all