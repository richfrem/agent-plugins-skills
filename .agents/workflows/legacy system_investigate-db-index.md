---
description: Reusable analysis module for Oracle Database Indexes. Called by `/codify-db-index`.
---

---
description: Reusable analysis module for Oracle Database Indexes. Called by `/codify-db-index`.
inputs: [IndexName]
tier: 2
# /investigate-db-index

**Purpose:** Reusable analysis module for Oracle Database Indexes. Called by `/codify-db-index`.




## Phase 1: Context Initialization

### Step 1: Initialize Context
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [IndexName] --type index
### Step 2: Locate Index Source
```bash
find_by_name --pattern "*[IndexName]*.sql" --directory legacy-system/oracle-database/Indexes
## Phase 2: Recursive Context Spiral
> **Direction: DOWNSTREAM ONLY (up to 3 levels)**

1. **Trace:** `python scripts/dependencies.py --target [IndexName] --deep --direction downstream --json`
2. **Action:** Identify target table, columns indexed.

## Phase 3: Mining

### Step 3: Extract Index Details
- Index type (B-Tree, Bitmap, Function-based)
- Target table and columns
- Unique/Non-unique

### Step 4: Run DB Miner
```bash
python scripts/db_miner.py --target [IndexName]
## Phase 4: Dependency & Lineage Analysis

### Step 5: System-Wide Check
```bash
python scripts/dependencies.py --target [IndexName] --deep --direction both
### Step 6: Application Discovery
```bash
python scripts/generate_applications_inventory.py --target [IndexName]
### Step 7: Lineage Check
```bash
/investigate-lineage [IndexName]
### Step 8: Completeness Checklist
- [ ] Index DDL
- [ ] Target table
- [ ] Columns
- [ ] Type (B-Tree/Bitmap/etc.)

## Output
- Context bundle (`temp/context-bundles/[IndexName]_context.md`)

**Called By:** `/codify-db-index`

// turbo-all