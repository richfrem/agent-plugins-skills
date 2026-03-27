---
description: Searches knowledge bases to ensure a Business Workflow does not already exist, the...
---

---
description: Searches knowledge bases to ensure a Business Workflow does not already exist, the...
tier: 1
# /investigate-business-workflow

**Command:** `/investigate-business-workflow [Keyword]`

**Purpose:** Searches knowledge bases to ensure a Business Workflow does not already exist, then recursively builds context (Forms, Libraries, DB) to verify the process logic.

**This is a COMPOUND, RECURSIVE workflow.**

## Phase 1: Context Initialization

### Step 1: Initialize Context (Smart Context)
Start a fresh bundle for this investigation topic.
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target "topic_[Slug]" --type custom
```
*   **Output:** `temp/manifests/custom_topic_[Slug]_manifest.json`

### Step 2: Seed Search
Query the knowledge base for existing candidates to populate the initial manifest.
```bash
python scripts/search_plsql.py "[Keyword]"
```
*   **Action:** If results found, add them to the manifest.
    ```bash
    python .agent/skills/context-bundler/scripts/manifest_manager.py add --path "legacy-system/business-rules/BW-XXXX.md" --note "Existing Candidate" --manifest "temp/manifests/custom_topic_[Slug]_manifest.json"
    ### Step 3: Confirmation Search (RLM & Vector)
Cross-reference against the Intelligence Layer to catch uncategorized workflows.
```bash
# Check RLM Cache for existing summaries

# Check Vector Database for semantic matches
## Phase 2: Recursive Verification Loop (The "Context Spiral")

> **Objective:** Recursively expand the context by tracing dependencies (Forms, Libraries, Packages) that implement this workflow.
> **Protocol:** Repeat steps until the context is complete.

### Stop Condition & Iteration Limit
- **Max Iterations:** 3 Loop Cycles.
- **Error:** If context is still incomplete after 3 cycles, STOP. Do not loop infinitely.

```
┌─────────────────────────────────────────────────────────┐
│                    RECURSION LOOP                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Review  │───►│ Add File │───►│ Rebundle │───┐       │
│  │  Bundle  │◄───┴──────────┴────┴──────────┘   │       │
│  └────┬─────┘                                   │       │
│       │ Context Complete?                       │       │
│       ▼                                         │       │
│   [YES: Proceed to Decision]  [NO: Loop]────────┘       │
└─────────────────────────────────────────────────────────┘
### Level 1: Process Logic (The Core)
1.  **Generate Bundle:**
    ```bash
    python .agent/skills/context-bundler/scripts/manifest_manager.py bundle --manifest "temp/manifests/custom_topic_[Slug]_manifest.json"
    ```
2.  **Review `[Slug]_context.md`:** Look for references to:
    -   Multiple Forms involved in the flow (Navigation).
    -   Shared Libraries (`JUSLIB`, `JRS_LIB`) containing status/state logic.
    -   Key Database Packages (State Managers).
3.  **If ANY are missing:**
    -   **Add:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path relative/path/to/file --note "Workflow Dependency"`
    -   **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`
    -   **Repeat** until core logic is captured.

### Level 2: Downstream Verification
1.  **Trace:** If specific DB Tables/Views are central to the workflow (e.g. `JUS_CASES`), ensure their schema definition is included.
2.  **Add/Rebundle** if missing.

## Phase 3: Decision Matrix

**Outcome A: Update (Match Found)**
*   **Result:** The workflow ALREADY exists (`BW-XXXX`).
*   **Action:** Proceed to Phase 2b to **Augment**.

**Outcome B: Create (New Logic)**
*   **Result:** Process logic found but NO codified workflow exists.
*   **Action:** Proceed to Phase 2 to **Register**.

**Outcome C: Stop (No Logic)**
*   **Result:** No existing workflow and no code evidence found.
*   **Action:** Halt process.

**Outcome D: Consolidate (Duplicates)**
*   **Result:** Multiple existing workflows cover the same process.
*   **Action:** Create a consolidation task.