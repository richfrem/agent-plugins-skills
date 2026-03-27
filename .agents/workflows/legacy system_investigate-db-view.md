---
description: Complete reusable analysis module for Oracle Database Views. Handles context initi...
---

---
description: Complete reusable analysis module for Oracle Database Views. Handles context initi...
inputs: [ViewName]
tier: 2
# /investigate-db-view

**Purpose:** Complete reusable analysis module for Oracle Database Views. Handles context initialization, recursive discovery, and view logic analysis. Called by `/codify-db-view` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [ViewName] --type view
```
*Output:* `temp/context-bundles/[ViewName]_context.md`

### Step 2: Locate View Source
```bash
find_by_name --pattern "*[ViewName]*.sql" --directory legacy-system/oracle-database/Views
### Step 3: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[ViewName]_context.md
## Phase 2: Recursive Verification Loop (The "Context Spiral")
> **Direction: DOWNSTREAM ONLY during recursion (up to 3 levels)**

### Level 1: Core Content (The View Definition)
- Verify bundle contains the full view SQL.

### Level 2: Base Tables
1. **Trace:** Run dependency CLI:
   ```bash
   python scripts/dependencies.py --target [ViewName] --deep --direction downstream --json
   ```
2. **Action:** Identify base tables and other views referenced.
   - **Command:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path ...`
   - **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`

## Phase 3: Mining (The Detective)

### Step 4: Extract View Logic
- SELECT columns, JOINs, WHERE conditions
- Security predicates (Row Level Security)

### Step 5: Run DB Miner
```bash
python scripts/db_miner.py --target [ViewName]
### Step 6: Search for Security Patterns
```bash
python scripts/search_plsql.py --target [ViewName] --pattern "SYS_CONTEXT|USERENV|WHERE"
## Phase 4: Dependency & Lineage Analysis

### Step 7: System-Wide Dependency Check
```bash
python scripts/dependencies.py --target [ViewName] --deep --direction both
### Step 8: Application Discovery (Parent Modules)
```bash
python scripts/generate_applications_inventory.py --target [ViewName]
### Step 9: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [ViewName]
### Step 10: Context Completeness Checklist
- [ ] View SQL source
- [ ] Base tables identified
- [ ] Security predicates (RLS)
- [ ] Upstream callers identified

## Output
- Populated context bundle (`temp/context-bundles/[ViewName]_context.md`)

**Called By:**
- `/codify-db-view` → Uses output to fill documentation template

// turbo-all