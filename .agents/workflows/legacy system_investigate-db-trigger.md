---
description: Complete reusable analysis module for Oracle Database Triggers. Handles context in...
---

---
description: Complete reusable analysis module for Oracle Database Triggers. Handles context in...
inputs: [TriggerName]
tier: 2
# /investigate-db-trigger

**Purpose:** Complete reusable analysis module for Oracle Database Triggers. Handles context initialization, recursive discovery, and trigger logic analysis. Called by `/codify-db-trigger` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [TriggerName] --type trigger
```
*Output:* `temp/context-bundles/[TriggerName]_context.md`

### Step 2: Locate Trigger Source
```bash
find_by_name --pattern "*[TriggerName]*.sql" --directory legacy-system/oracle-database/Triggers
### Step 3: Review Bundle
```bash
view_file temp/context-bundles/[TriggerName]_context.md
## Phase 2: Recursive Verification Loop (The "Context Spiral")
> **Direction: DOWNSTREAM ONLY during recursion (up to 3 levels)**

### Level 1: Core Content (The Trigger)
- Verify bundle contains the full trigger SQL.

### Level 2: Target Table and Dependencies
1. **Trace:** Run dependency CLI:
   ```bash
   python scripts/dependencies.py --target [TriggerName] --deep --direction downstream --json
   ```
2. **Action:** Identify target table, referenced packages, other tables.

## Phase 3: Mining (The Detective)

### Step 4: Extract Trigger Signature
- Timing: BEFORE/AFTER/INSTEAD OF
- Event: INSERT/UPDATE/DELETE
- Target table

### Step 5: Run DB Miner
```bash
python scripts/db_miner.py --target [TriggerName]
### Step 6: Search for Business Rules
```bash
python scripts/search_plsql.py --target [TriggerName] --pattern "RAISE_APPLICATION_ERROR|:NEW|:OLD"
## Phase 4: Dependency & Lineage Analysis

### Step 7: System-Wide Dependency Check
```bash
python scripts/dependencies.py --target [TriggerName] --deep --direction both
### Step 8: Application Discovery
```bash
python scripts/generate_applications_inventory.py --target [TriggerName]
### Step 9: Lineage Check
```bash
/investigate-lineage [TriggerName]
### Step 10: Context Completeness Checklist
- [ ] Trigger SQL source
- [ ] Target table identified
- [ ] Business rules (validations)
- [ ] Referenced packages/procedures

## Output
- Populated context bundle (`temp/context-bundles/[TriggerName]_context.md`)
- Validation rule candidates
- **Code Generator Handoff**: When generating migration scripts or test harnesses based on this analysis, the agent MUST format the output using the "Modular Building Blocks" architecture (separating convenience CLI wrappers from core functional Python/SQL APIs).
**Called By:**
- `/codify-db-trigger` → Uses output to fill documentation template

// turbo-all