---
description: Searches knowledge bases to ensure a Business Rule does not already exist, then re...
---

---
description: Searches knowledge bases to ensure a Business Rule does not already exist, then re...
tier: 1
# /investigate-business-rule

**Command:** `/investigate-business-rule [Keyword]`

**Purpose:** Searches knowledge bases to ensure a Business Rule does not already exist, then recursively builds context (Forms, Libraries, DB) to verify the distributed logic.

**This is a COMPOUND, RECURSIVE workflow.**

## Phase 1: Context Initialization

### Step 1: Initialize Topic Context
Start a fresh bundle for this investigation topic.
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target "topic_[Slug]" --type custom
```
*   **Output:** `temp/manifests/custom_topic_[Slug]_manifest.json`

### Step 2: Seed Search
Query the knowledge base for existing candidates.
```bash
python scripts/search_plsql.py "[Keyword]"
```
*   **Action:** If results found, add them to the manifest.
    ```bash
    python .agent/skills/context-bundler/scripts/manifest_manager.py add --path "legacy-system/business-rules/BR-XXXX.md" --note "Existing Candidate" --manifest "temp/manifests/custom_topic_[Slug]_manifest.json"
    ### Step 3: Confirmation Search (RLM & Vector)
Cross-reference against the Intelligence Layer to catch uncategorized logic.
```bash
# Check RLM Cache for existing summaries

# Check Vector Database for semantic matches
## Phase 2: Recursive Verification Loop (The "Context Spiral")

> **Objective:** Recursively discover dependencies (Forms, Libraries, DB Objects) that implement this rule logic.
> **Constraint:** Limit downstream analysis to **Max 3 Levels** from the initial finding.

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
### Level 1: Rule Logic (The Core)
1.  **Generate Bundle:**
    ```bash
    python .agent/skills/context-bundler/scripts/manifest_manager.py bundle --manifest "temp/manifests/custom_topic_[Slug]_manifest.json"
    ```
2.  **Review `[Slug]_context.md`:** Look for:
    -   **Triggers:** `WHEN-VALIDATE-ITEM`, `PRE-INSERT`.
    -   **Libraries:** Shared validation procedures.
    -   **DB Constraints:** Check constraints or trigger logic.
3.  **If ANY are missing:**
    -   **Add:** `python .agent/skills/context-bundler/scripts/manifest_manager.py add --path relative/path/to/file --note "Rule Logic"`
    -   **Rebundle:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle`
    -   **Repeat** until logic source is captured.

### Level 2: Downstream Verification
1.  **Trace:** If the rule relies on DB functions or View definitions, ensure they are included.
2.  **Add/Rebundle** if missing.

## Phase 3: Decision Matrix

**Outcome A: Update (Match Found)**
*   **Result:** The rule ALREADY exists (`BR-XXXX`).
*   **Action:** Proceed to Phase 2b to **Augment**.

**Outcome B: Create (New Logic)**
*   **Result:** Code found but NO rule exists.
*   **Action:** Proceed to Phase 2 to **Register**.

**Outcome C: Stop (No Logic)**
*   **Result:** No existing rule and no code evidence found.
*   **Action:** Halt process.

**Outcome D: Consolidate (Duplicates)**
*   **Result:** Multiple existing rules cover the same logic.
*   **Action:** Create a consolidation task.