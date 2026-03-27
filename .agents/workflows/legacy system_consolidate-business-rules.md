---
description: Workflow for merging and consolidating duplicate Business Rules (Outcome D).
inputs: [Topic, MasterID (Optional), ListOfDuplicates]
---

**When to use:**
Use this workflow when **Outcome D (Duplicates Found)** is triggered by `/investigate-business-rule`.
Detailed usage happens in a dedicated `consolidate-rules-[Topic]` task.

**Goal:** Clean up the knowledge base by merging multiple `BR-XXXX` files into a single authoritative source.

---

## Phase 0: Pre-Flight (The Gate)

```bash
/agent-orchestrator_plan "consolidate-business-rules-[Target]"
```

**What this does:**
1.  **Context Check**: Verifies git branch and environment.
2.  **SDD Lifecycle**: Executes `/spec-kitty.specify` -> `/spec-kitty.plan` -> `/spec-kitty.tasks`.

> **⚠️ STOP:** Do not proceed to Phase 1 until the Orchestrator confirms the plan and tasks are generated.

---

## Phase 0.5: Create Worktree (MANDATORY for Clean Merge)

> **⚠️ CRITICAL**: This step creates the isolated workspace that enables `spec-kitty merge` to work properly.

### Step 1a: Create Implementation Worktree
```bash
spec-kitty implement WP01
```
*This handles: Git state check, context alignment, spec/branch management.*

## Phase 1: Analysis & Selection

### Step 1: List Candidates
Identify all files covering the same topic.
```bash
/inventory-manager_curate-inventories --search "[Keyword]"
```
# Output example:
# BR-0010: Publication Ban (Complete)
# BR-0045: Pub Ban Logic (Partial)
# BR-0102: Ban Check (Duplicate)

### Step 2: Select Master Rule
Choose the **Master**:
-   **Criteria 1**: The most complete/detailed rule.
-   **Criteria 2**: The lowest ID (oldest) if content is similar.
-   **Criteria 3**: If none are good, create a NEW one (`BR-NEW`) and act as if others are legacy.

**Decision:**
-   **Master:** `BR-XXXX`
-   **Losers:** `BR-YYYY`, `BR-ZZZZ`

### Step 2b: Confirm Strategy with User (Mandatory)
Before merging or deleting anything:
1.  **Present Plan:** "I propose making `BR-XXXX` the Master and deprecating `BR-YYYY`."
2.  **Wait for Approval:** Do NOT proceed until the user says "Go ahead".

---

## Phase 2: Content Merger

### Step 3: Enriched Master
Read the "Loser" files. If they contain unique context (e.g., specific triggers or source links) not in the Master, transfer it.
-   **Action:** Update `BR-XXXX` (Master).
-   **Command:** `/legacy-system-business-rules_investigate-business-rule --update --id [MasterID] --summary "Consolidated with [LoserID]"` (then manual edit).

---

## Phase 3: Deprecation (The Redirect)

### Step 4: Mark Losers as Deprecated
Edit each "Loser" file (`BR-YYYY`, `BR-ZZZZ`).
1.  **Status**: Change to `Deprecated`.
2.  **Redirect**: Add a prominent link to the Master.

**Template:**
```markdown
# BR-YYYY: [Old Title]

> [!WARNING]
> **DEPRECATED / DUPLICATE**
> This rule has been consolidated.
> **See Authoritative Rule:** [[BR-XXXX]]

## Metadata
...
```

---

## Phase 4: Reference Updates (The Cleanup)

### Step 5: Update External References
Find where the "Loser" rules were cited (e.g., in Form Overviews).
```bash
# Search for the ID
grep -r "BR-YYYY" legacy-system/oracle-forms-overviews/
```

**Action:**
-   Replace `[[BR-YYYY]]` with `[[BR-XXXX]]`.
-   Or update the table row to point to the new ID.

---

### Step 6: Update Knowledge Base
Refresh the system to recognize the Master and ignore/flag the Deprecated ones.
```bash
/inventory-manager_curate-inventories
```

### Step 7: Closure
```bash
/agent-orchestrator_retro
/spec-kitty.merge
```

// turbo-all
