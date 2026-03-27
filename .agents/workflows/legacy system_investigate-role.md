---
description: Deep dive analysis of a *single* user role (e.g., `JCS_SYSADMIN`). Uses an iterati...
---

---
description: Deep dive analysis of a *single* user role (e.g., `JCS_SYSADMIN`). Uses an iterati...
tier: 1
# /investigate-role

**Command:** `/investigate-role [RoleName]`

**Purpose:** Deep dive analysis of a *single* user role (e.g., `JCS_SYSADMIN`). Uses an iterative context bundling approach to aggregate Inventory status, PL/SQL usage, Menu access, and related artifacts into a complete context bundle.

**This is a COMPOUND, RECURSIVE workflow.**

**Called By:** `/codify-role`, `/investigate-form-roles`, `/codify-form`

## Phase 1: Foundation (Inventory & Init)

### Step 1: Inventory Verification
Check if the role exists in the Authoritative Source.

```bash
python scripts/split_roles.py "[RoleName]"
```
*   **Active:** Role is valid and current.
*   **Legacy/Deprecated:** Check `roles_inventory.json` directly if unsure.
*   **Unknown:** Logic finding might be a candidate for a new role or typo.

### Step 2: Initialize Context Manifest
Start a fresh context bundle for this role investigation.

```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target "[RoleName]" --type role
```
*   **Creates:** `temp/manifests/role_[RoleName]_manifest.json`
*   **Base:** `../skills/legacy-system-roles/assets/base-role-manifest.json`
*   **Includes:** `roles_inventory.json`

## Phase 2: Recursive Verification Loop (The "Context Spiral")

> **Objective:** Execute multiple search strategies to find *every* artifact (Form, Library, Report, Config) that references this role. As you find files, add them to the manifest.

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
│   [YES: Proceed to Analysis]  [NO: Loop]────────┘       │
└─────────────────────────────────────────────────────────┘
### Step 3: Run Miners
Execute these commands to identify relevant files. Use the `Role` as the search term.

#### A. PL/SQL Search (Code Logic)
Find explicit checks like `:GLOBAL.[Role]` or string literals.
```bash
# 1. Attribute Search (Primary)
python tools/investigate/search/findPLSQLTermAttributeKeyword.py --term "[RoleName]"

# 2. Pattern Search (Secondary)
python scripts/search_plsql.py --term ":GLOBAL.[RoleName]"
#### B. Pre-Computed & Configuration Search
Check the specific CSVs using dedicated role search tools.
```bash
# 1. Button Visibility
python tools/investigate/search/search_button_rules.py "[RoleName]" --json > temp/role_[RoleName]_buttons.json

# 2. Menu Access
python tools/investigate/search/search_menu_rules.py "[RoleName]" --json > temp/role_[RoleName]_menus.json

# 3. Report Associations (Role Search)
python tools/investigate/search/search_report_rules.py "[RoleName]" --type role --json > temp/role_[RoleName]_reports.json

# Legacy Batch Summaries & Intelligence Search
# Check RLM Cache for existing summaries

# Check Vector Database for semantic matches
### Step 4: Iterative Mining & Repackaging (The Loop)
**Review the Output from Step 3.** Identify candidate files where the Role is used.
Run the appropriate **Miner** to extract structured context (Logic, Triggers, Dependencies) from the source.

#### A. Forms (FMB/XML)
If a Form is found (e.g., `JCSE0030`), extract its logic:
```bash
python scripts/xml_miner.py --target "[FormID]"
# Add the miner output to manifest
python .agent/skills/context-bundler/scripts/manifest_manager.py add --path "temp/[FormID]_mined.md" --note "Form Logic for [RoleName]" --manifest "temp/manifests/role_[RoleName]_manifest.json"
#### B. Libraries (PLL)
If a Library is found (e.g., `JUSLIB`), extract its API and Global logic:
```bash
python scripts/pll_miner.py --target "[LibName]"
python .agent/skills/context-bundler/scripts/manifest_manager.py add --path "temp/[LibName]_mined.md" --note "Library Logic" --manifest "temp/manifests/role_[RoleName]_manifest.json"
#### C. Menus (MMB)
If a Menu is customized:
```bash
python scripts/menu_xml_miner.py --target "[MenuName]"
python .agent/skills/context-bundler/scripts/manifest_manager.py add --path "temp/[MenuName]_mined.md" --note "Menu Structure" --manifest "temp/manifests/role_[RoleName]_manifest.json"
#### D. Reports & DB
Use `report_miner.py` or `db_miner.py` if relevant artifacts are discovered.

> **Loop Rule:** If the Miner output reveals *new* dependencies (e.g. Form A calls Lib B), repeat the search/mine process for those new targets.
> **Action:** `python .agent/skills/context-bundler/scripts/manifest_manager.py bundle` (Re-bundle after adding)

## Phase 3: Final Bundle & Analysis

### Step 5: Final Bundle Generation
Once discovery is exhaustive, create the final bundle for analysis.

```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py bundle --manifest "temp/manifests/role_[RoleName]_manifest.json"
```
> **Output:** `temp/context-bundles/role_[RoleName]_context.md`

### Step 6: Analysis (The "Ask")
Use the bundled context to answer the questions in the prompt.

**Open the Bundle:**
```bash
view_file temp/context-bundles/role_[RoleName]_context.md
**Perform Analysis:**
1.  **Synthesize Description:** User persona and responsibilities.
2.  **Extract Applications:** List all unique `APP_CD` (Applications) this role touches.
3.  **Extract Capabilities:** Specific privileges guarded by this role.
4.  **Map All Access:**
     *   **Forms:** Aggregated list from Menus, Buttons, and explicit PL/SQL logic.