---
description: Rebuilds the master_object_collection.json from all individual inventories.
tier: 1
---

**When to use:** After creating/updating documentation (forms, business rules, etc.) to refresh the unified object index.

**What it does:**
- Aggregates all individual inventories (forms, reports, tables, roles, etc.) into `legacy-system/reference-data/master_object_collection.json`.
- Resolves artifact paths (overview, xml, sql) and verifies they exist.
- Used by link enrichment and the Oracle Forms Visualizer.

**Command:**
```bash
python scripts/build_master_collection.py --full
```
// turbo

---


## Phase 0: Pre-Flight (MANDATORY)

> **IMPORTANT**: You MUST be on `main` branch before running spec-kitty.
> Spec-kitty will create the feature branch automatically.

```bash
# (Git operations removed - handled by spec-kitty)

# 2. Create feature (creates branch + folder in kitty-specs/)
spec-kitty agent feature create-feature "curate-update-inventory-[Target]" --json
```
*This handles: Git state check, context alignment, spec/branch management.*

## Phase 2: Mandatory Self-Retrospective and Continuous Improvement Loop
> **STOP AND REFLECT:** This is a critical step for system evolution.

### Step 3: Workflow Smoothness Check
How many times did you have to correct yourself or retry a step?
- [ ] **0-1 Retries**: Smooth.
- [ ] **2+ Retries**: Bumpy. (Explain why below)

### Step 4: Tooling & Documentation Gap Analysis
- [ ] Did `build_master_collection.py` fail?
- [ ] Were any CLI outputs confusing or hard to parse?

### Step 5: Immediate Improvement (The "Boy Scout Rule")
**You MUST strictly choose one action:**
- [ ] **Option A (Fix Code)**: I will fix a script bug identified in this run. (Do it now).
- [ ] **Option B (Fix Docs)**: I will clarify a confusing step in THIS workflow file (`curate-update-inventory.md`). (Do it now).
- [ ] **Option C (New Task)**: The issue is too big for now. I will create a new Task to address it later.
- [ ] **Option D (No Issues)**: The workflow was flawless. (Rare).

**Execution:**
Perform the selected improvement **BEFORE** marking this task as Done.

