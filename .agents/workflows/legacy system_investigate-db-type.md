---
description: Reusable analysis module for Oracle Database Types. Called by `/codify-db-type`.
---

---
description: Reusable analysis module for Oracle Database Types. Called by `/codify-db-type`.
inputs: [TypeName]
tier: 2
# /investigate-db-type

**Purpose:** Reusable analysis module for Oracle Database Types. Called by `/codify-db-type`.




## Phase 1: Context Initialization

### Step 1: Initialize Context
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [TypeName] --type type
### Step 2: Locate Type Source
```bash
find_by_name --pattern "*[TypeName]*.sql" --directory legacy-system/oracle-database/Types
## Phase 2: Recursive Context Spiral
> **Direction: DOWNSTREAM ONLY (up to 3 levels)**

1. **Trace:** `python scripts/dependencies.py --target [TypeName] --deep --direction downstream --json`
2. **Action:** Identify nested types, referenced tables.

## Phase 3: Mining

### Step 3: Extract Type Details
- Type kind (OBJECT, COLLECTION, RECORD)
- Attributes/fields
- Methods (for OBJECT types)

### Step 4: Run DB Miner
```bash
python scripts/db_miner.py --target [TypeName]
## Phase 4: Dependency & Lineage Analysis

### Step 5: System-Wide Check
```bash
python scripts/dependencies.py --target [TypeName] --deep --direction both
### Step 6: Application Discovery
```bash
python scripts/generate_applications_inventory.py --target [TypeName]
### Step 7: Lineage Check
```bash
/investigate-lineage [TypeName]
### Step 8: Completeness Checklist
- [ ] Type DDL
- [ ] Kind (OBJECT/COLLECTION/RECORD)
- [ ] Attributes
- [ ] Usage locations

## Output
- Context bundle (`temp/context-bundles/[TypeName]_context.md`)

**Called By:** `/codify-db-type`

// turbo-all