---
description: Complete reusable analysis module for Oracle Database Packages. Handles context in...
---

---
description: Complete reusable analysis module for Oracle Database Packages. Handles context in...
inputs: [PackageName]
tier: 2
# /investigate-db-package

**Purpose:** Complete reusable analysis module for Oracle Database Packages. Handles context initialization, recursive discovery, and API/logic analysis. Called by `/codify-db-package` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [PackageName] --type package
```
*Action:* Resets manifest, loads base Package manifest, populates dependencies.
*Output:* `temp/context-bundles/[PackageName]_context.md` (Generated Bundle)

### Step 2: Locate Package Source
```bash
find_by_name --pattern "*[PackageName]*.sql" --directory legacy-system/oracle-database/source/Packages
```
*Identify the target package file path (may have separate spec/body files).*

### Step 3: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[PackageName]_context.md
view_file legacy-system/oracle-db-overviews/packages/[PackageName]-Package-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (SQL spec and body)?
2. Does it have RLM summaries for key calling objects?

## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Diagram:** `../skills/legacy-system-database/references/diagrams/workflows/db-package-discovery.mmd`
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
### Level 1: Core Content (The Source)
- Verify `[PackageName]_context.md` contains the full package SQL (spec and body).

### Level 2: Downstream Dependencies (Tables/Views/Packages Called)
1. **Trace:** Run dependency CLI:
   ```bash
   python scripts/dependencies.py --target [PackageName] --deep --direction downstream --json
   ```
2. **Action:** Identify tables, views, or other packages the package calls.
   - **Command:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path ...`
   - **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`
   - **Repeat** if more dependencies discovered.

### Level 3: Sub-Package Dependencies
1. **Trace:** Check for calls to other packages or functions:
   ```bash
   python scripts/search_plsql.py --target [PackageName] --pattern "PACKAGE|PROCEDURE|FUNCTION"
   ```
2. **Action:** Add related packages to manifest if critical.

*Stop Condition:* Proceed ONLY when context contains Source, Tables/Views, and key Package dependencies.

## Phase 3: Mining (The Detective)

### Step 4: Extract Public API (Specification)
From the spec, identify all public PROCEDURE and FUNCTION declarations:
```bash
python scripts/search_plsql.py --target [PackageName] --pattern "PROCEDURE|FUNCTION"
### Step 5: Run DB Miner
```bash
python scripts/db_miner.py --target [PackageName]
```
*Extracts: Procedures, Functions, Types, Table references, Error handling.*

### What It Extracts

| Category | Extraction Target | Modern Mapping |
|----------|------------------|----------------|
| **Public API** | Procedures/Functions in spec | Service API endpoints |
| **Internal Units** | Private procedures | Helper functions |
| **Tables** | SELECT/INSERT/UPDATE targets | Data layer dependencies |
| **Validation** | RAISE_APPLICATION_ERROR | Business rules |
| **Security** | CHECK_ROLE, SYS_CONTEXT | Authorization patterns |
| **Complexity** | Unit count, LOC | Refactoring difficulty |

### Step 6: Search for Business Rules
```bash
python scripts/search_plsql.py --target [PackageName] --pattern "RAISE_APPLICATION_ERROR|EXCEPTION"
```
*Identifies validation logic and error conditions.*

### Step 7: Search for Security Patterns
```bash
python scripts/search_plsql.py --target [PackageName] --pattern "CHECK_ROLE|GLOBAL\\.|SYS_CONTEXT"
```
*Identifies role checks and security patterns.*

## Phase 4: Dependency & Lineage Analysis

### Step 8: System-Wide Dependency Check
```bash
python scripts/dependencies.py --target [PackageName] --deep --direction both
### Step 9: Application Discovery (Parent Modules)
```bash
python scripts/generate_applications_inventory.py --target [PackageName]
```
*Identifies which applications/forms use this package.*

### Step 10: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [PackageName]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

### Step 11: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source Code (SQL spec and body)
- [ ] Public API inventory (procedures/functions)
- [ ] Downstream dependencies (tables, views, packages)
- [ ] Upstream callers identified
- [ ] Application context identified
- [ ] Business rule candidates flagged
- [ ] Security patterns documented

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[PackageName]_context.md`)
- Console output with API inventory and patterns
- Validation rule candidates
- Security pattern documentation
- **Code Generator Handoff**: When generating migration scripts or test harnesses based on this analysis, the agent MUST format the output using the "Modular Building Blocks" architecture (separating convenience CLI wrappers from core functional Python/SQL APIs).

**Called By:**
- `/codify-db-package` → Uses output to fill documentation template

**See Also:**
- `dependencies.py --target [PackageName] --deep --json` - Get dependencies with file paths
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ total)
- `/investigate-db-procedure` - For standalone procedures
- `/investigate-db-function` - For standalone functions

// turbo-all