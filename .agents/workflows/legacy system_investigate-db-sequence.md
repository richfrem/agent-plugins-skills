---
description: Reusable analysis module for Oracle Database Sequences. Called by `/codify-db-sequ...
---

---
description: Reusable analysis module for Oracle Database Sequences. Called by `/codify-db-sequ...
inputs: [SequenceName]
tier: 2
# /investigate-db-sequence

**Purpose:** Reusable analysis module for Oracle Database Sequences. Called by `/codify-db-sequence`.




## Phase 1: Context Initialization

### Step 1: Initialize Context
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [SequenceName] --type sequence
### Step 2: Locate Sequence Source
```bash
find_by_name --pattern "*[SequenceName]*.sql" --directory legacy-system/oracle-database/Sequences
## Phase 2: Recursive Context Spiral
> **Direction: DOWNSTREAM ONLY (up to 3 levels)**

1. **Trace:** `python scripts/dependencies.py --target [SequenceName] --deep --direction downstream --json`

## Phase 3: Mining

### Step 3: Extract Sequence Details
- START WITH, INCREMENT BY
- MIN/MAX VALUE
- CYCLE/NOCYCLE
- CACHE

### Step 4: Find Usage
```bash
python scripts/search_plsql.py --target [SequenceName] --pattern "NEXTVAL|CURRVAL"
## Phase 4: Dependency & Lineage Analysis

### Step 5: System-Wide Check
```bash
python scripts/dependencies.py --target [SequenceName] --deep --direction both
### Step 6: Application Discovery
```bash
python scripts/generate_applications_inventory.py --target [SequenceName]
### Step 7: Lineage Check
```bash
/investigate-lineage [SequenceName]
### Step 8: Completeness Checklist
- [ ] Sequence DDL
- [ ] Properties (start, increment)
- [ ] Usage locations (NEXTVAL callers)

## Output
- Context bundle (`temp/context-bundles/[SequenceName]_context.md`)

**Called By:** `/codify-db-sequence`

// turbo-all