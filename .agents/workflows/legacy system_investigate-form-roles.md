---
description: Ensures that every Role checked or used within a specific Form is fully documented...
---

---
description: Ensures that every Role checked or used within a specific Form is fully documented...
tier: 2
# /investigate-form-roles

**Command:** `/investigate-form-roles [FormID]`

**Purpose:** Ensures that every Role checked or used within a specific Form is fully documented. It discovers roles in the form source and recursively calls `/codify-role` for each one.

**This is a LOOPER/ITERATOR workflow.**

**Called By:** `/codify-form`



## Phase 1: Discovery

### Step 1: Identify Role Candidates
Mines the target form for any role-like strings or global variables.

```bash
# 1. Search for Global Role Checks in the Form
python scripts/search_plsql.py --target "[FormID]" --term ":GLOBAL.[A-Z_]+" > temp/[FormID]_role_candidates.txt

# 2. Search for String Literals (e.g. 'JCS_ADMIN')
python scripts/search_plsql.py --target "[FormID]" --pattern "'[A-Z_]{4,}'" >> temp/[FormID]_role_candidates.txt
### Step 2: Correlate with Inventory
Filter the raw list against the `roles_inventory.json` (or `legacy-system/justin-roles/`) to confirm which candidates are actual Roles.
*   *Note:* You may use `../skills/legacy-system-roles/scripts/split_roles.py` in a loop or a custom script if available.

## Phase 2: Execution Loop

### Step 3: Iterate and Codify
For each **UNIQUE, VERIFIED** Role found in Step 2:

1.  **Check Sensitivity:** Is this the first time this role is being documented in this session?
2.  **Execute:**
    ```bash
    /codify-role [RoleName]
    ```
    *(This triggers the deep dive, manifest creation, and documentation update for that role)*

> **Optimization:** If a Role has already been codified recently (check `legacy-system/justin-roles/[Role].md` timestamp), you may skip it to save time, UNLESS you believe this Form adds critical new context.

## Phase 3: Summary

### Step 4: Report
List which Roles were processed and their status.

*   **Documented:** [JCS_ADMIN, JCS_VIEW]
*   **Skipped:** [Others]
*   **Unknown/New:** [Any strings that looked like roles but weren't in inventory?]