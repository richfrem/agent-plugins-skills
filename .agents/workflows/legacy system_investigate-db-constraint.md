---
description: Reusable analysis module for Oracle Database Constraints. Called by `/codify-db-co...
---

---
description: Reusable analysis module for Oracle Database Constraints. Called by `/codify-db-co...
inputs: [ConstraintName]
tier: 2
# /investigate-db-constraint

**Purpose:** Reusable analysis module for Oracle Database Constraints. Called by `/codify-db-constraint`.




## Phase 1: Context Initialization

### Step 1: Initialize Context
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [ConstraintName] --type constraint
### Step 2: Locate Constraint Source
```bash
find_by_name --pattern "*[ConstraintName]*.sql" --directory legacy-system/oracle-database/Constraints
## Phase 2: Recursive Context Spiral
> **Direction: DOWNSTREAM ONLY (up to 3 levels)**

1. **Trace:** `python scripts/dependencies.py --target [ConstraintName] --deep --direction downstream --json`
2. **Action:** Identify target table, referenced table (FK).

## Phase 3: Mining

### Step 3: Extract Constraint Details
- Type (PK, FK, CHECK, UNIQUE, NOT NULL)
- Target table and columns
- Referenced table (for FK)
- Condition (for CHECK)

### Step 4: Run DB Miner
```bash
python scripts/db_miner.py --target [ConstraintName]
## Phase 4: Dependency & Lineage Analysis

### Step 5: System-Wide Check
```bash
python scripts/dependencies.py --target [ConstraintName] --deep --direction both
### Step 6: Application Discovery
```bash
python scripts/generate_applications_inventory.py --target [ConstraintName]
### Step 7: Lineage Check
```bash
/investigate-lineage [ConstraintName]
### Step 8: Completeness Checklist
- [ ] Constraint DDL
- [ ] Type
- [ ] Target table/columns
- [ ] Referenced table (FK)

## Output
- Context bundle (`temp/context-bundles/[ConstraintName]_context.md`)

**Called By:** `/codify-db-constraint`

// turbo-all