---
description: Complete reusable analysis module for Oracle Database Procedures. Handles context ...
---

---
description: Complete reusable analysis module for Oracle Database Procedures. Handles context ...
inputs: [ProcedureName]
tier: 2
# /investigate-db-procedure

**Purpose:** Complete reusable analysis module for Oracle Database Procedures. Handles context initialization, recursive discovery, and analysis. Called by `/codify-db-procedure` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [ProcedureName] --type procedure
```
*Action:* Resets manifest, loads base Procedure manifest, populates dependencies.
*Output:* `temp/context-bundles/[ProcedureName]_context.md` (Generated Bundle)

### Step 2: Locate Procedure Source
```bash
find_by_name --pattern "*[ProcedureName]*.sql" --directory legacy-system/oracle-database/Procedures
### Step 3: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[ProcedureName]_context.md
view_file legacy-system/oracle-db-overviews/procedures/[ProcedureName]-Procedure-Overview.md (if exists)
## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Objective:** Expand context by tracing dependencies downstream.

> **⚠️ Direction: DOWNSTREAM ONLY during recursion (up to 3 levels)**

### Level 1: Core Content (The Source)
- Verify `[ProcedureName]_context.md` contains the full procedure SQL source.

### Level 2: Downstream Dependencies
1. **Trace:** Run dependency CLI:
   ```bash
   python scripts/dependencies.py --target [ProcedureName] --deep --direction downstream --json
   ```
2. **Action:** Identify tables, views, or other objects the procedure calls.
   - **Command:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path ...`
   - **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`

*Stop Condition:* Proceed ONLY when context contains Source and key Dependencies.

## Phase 3: Mining (The Detective)

### Step 4: Extract Procedure Signature
- **Parameters**: Name, Type, IN/OUT mode
- **Purpose**: From comments or naming conventions

### Step 5: Run DB Miner
```bash
python scripts/db_miner.py --target [ProcedureName]
### Step 6: Search for Business Rules
```bash
python scripts/search_plsql.py --target [ProcedureName] --pattern "RAISE_APPLICATION_ERROR|EXCEPTION"
## Phase 4: Dependency & Lineage Analysis

### Step 7: System-Wide Dependency Check
```bash
python scripts/dependencies.py --target [ProcedureName] --deep --direction both
### Step 8: Application Discovery (Parent Modules)
```bash
python scripts/generate_applications_inventory.py --target [ProcedureName]
### Step 9: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [ProcedureName]
### Step 10: Context Completeness Checklist
- [ ] Source Code (SQL)
- [ ] Procedure signature
- [ ] Downstream dependencies
- [ ] Upstream callers identified
- [ ] Application context identified

## Output
- Populated context bundle (`temp/context-bundles/[ProcedureName]_context.md`)
- Validation rule candidates
- **Code Generator Handoff**: When generating migration scripts or test harnesses based on this analysis, the agent MUST format the output using the "Modular Building Blocks" architecture (separating convenience CLI wrappers from core functional Python/SQL APIs).

**Called By:**
- `/codify-db-procedure` → Uses output to fill documentation template

// turbo-all