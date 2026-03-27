---
description: Complete reusable analysis module for Oracle Database Tables. Handles context init...
---

---
description: Complete reusable analysis module for Oracle Database Tables. Handles context init...
inputs: [TableName]
tier: 2
# /investigate-db-table

**Purpose:** Complete reusable analysis module for Oracle Database Tables. Handles context initialization, recursive discovery, and schema analysis. Called by `/codify-db-table` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [TableName] --type table
```
*Output:* `temp/context-bundles/[TableName]_context.md`

### Step 2: Locate Table Source
```bash
find_by_name --pattern "*[TableName]*.sql" --directory legacy-system/oracle-database/Tables
### Step 3: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[TableName]_context.md
view_file legacy-system/oracle-db-overviews/tables/[TableName]-Table-Overview.md (if exists)
## Phase 2: Recursive Verification Loop (The "Context Spiral")
> **Direction: DOWNSTREAM ONLY during recursion (up to 3 levels)**

### Level 1: Core Content (The DDL)
- Verify bundle contains CREATE TABLE and constraints.

### Level 2: Related Schema Objects
1. **Trace:** Run dependency CLI:
   ```bash
   python scripts/dependencies.py --target [TableName] --deep --direction downstream --json
   ```
2. **Action:** Identify indexes, constraints, triggers, FK parent tables.
   - **Command:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path ...`
   - **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`

## Phase 3: Mining (The Detective)

### Step 4: Extract Table Schema
- Columns, data types, nullability
- Primary key, unique constraints
- Check constraints

### Step 5: Run DB Miner
```bash
python scripts/db_miner.py --target [TableName]
### Step 6: Find Related Triggers
```bash
python scripts/search_plsql.py --target [TableName] --pattern "BEFORE|AFTER|INSTEAD OF"
## Phase 4: Dependency & Lineage Analysis

### Step 7: System-Wide Dependency Check
```bash
python scripts/dependencies.py --target [TableName] --deep --direction both
### Step 8: Application Discovery (Parent Modules)
```bash
python scripts/generate_applications_inventory.py --target [TableName]
### Step 9: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [TableName]
### Step 10: Context Completeness Checklist
- [ ] Table DDL (columns, types)
- [ ] Constraints (PK, FK, CHECK, UNIQUE)
- [ ] Indexes
- [ ] Triggers
- [ ] Upstream callers identified
- [ ] FK relationships mapped

## Output
- Populated context bundle (`temp/context-bundles/[TableName]_context.md`)
- Schema object inventory

**Called By:**
- `/codify-db-table` → Uses output to fill documentation template

// turbo-all