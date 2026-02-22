---
trigger: always_on
---

# Oracle Library (PLL) Documentation Policy

> **Effective Date:** 2026-01-18
> **Related Standards:**
> *   [Form Documentation Policy](.agent/rules/legacy-system-analysis/form_documentation_policy.md)
> *   [Expert Persona](.agent/plugins/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md)

## 0. Objective
Establish a rigorous standard for documenting Oracle PL/SQL Libraries (PLLs). Unlike Forms (UI-centric), Libraries are **Logic-centric**. Documentation must focus on **API Contracts**, **Shared Logic**, and **Dependencies**.

## 1. Context Gathering (Mandatory RLM-First Protocol)
Before documenting a library, you must gather structured context using the CLI and RLM cache.

**Mandatory Sequence:**
1.  **Run Context Initialization**: 
    ```bash
    python plugins/cli.py context --target [LIB_NAME] --type lib
    ```
    *This resets the manifest and builds the initial bundle.*

2.  **Review Generated Context**: 
    - Open `temp/context-bundles/[LIB_NAME]_context.md`.
    - Check for `pll_miner` output and RLM summaries.
    - Check upstream usage (who calls me?).

3.  **Augment if Needed**:
    - If dependencies are missing, add them to `file-manifest.json` and regenerate.
5.  **Source Code**: 
    - Only deep-dive into `[LIB].txt` IF the RLM summary and Miner output leave specific questions unanswered.

## 2. Documentation Structure
All Library Overviews (`legacy-system/oracle-forms-overviews/libraries/[LIB]-Library-Overview.md`) must follow this structure:

### I. Header & Metadata
*   **Library Name**: e.g., `JUSLIB`
*   **Purpose**: One sentence summary (e.g., "General Utilities shared across all JUSTIN applications").
*   **Status**: `Active` or `Deprecated`.

### II. API Specification (The Contract)
List **ALL** packages, procedures, and functions exposed by the library.
*   **Format**: Table (Sort Alphabetically or by Package).
*   **Columns**: 
    1.  `Unit Name` (Hyperlinked to Source `../../oracle-forms-markdown/pll/[LIB].md#unit-name`)
    2.  `Type` (Procedure/Function)
    3.  `Description` (Brief summary)
*   **Source Truth**: Derived from `pll_miner.py` "PublicAPI" output.
*   **Requirement**: Must be exhaustive (Table of Contents style).

### III. Global State Management
Document any `GLOBAL` variables read or written.
*   **Recommendation**: Group variables by functionality (e.g., `AG$ALERT_*`, `JUS$_*`) if numerous.
*   **Critical**: Identify if the library is a "State Manager" (sets globals) or "Consumer" (reads globals).

### IV. Dependencies
*   **Called Forms**: Does it launch other screens? (`CALL_FORM`)
*   **DB Packages**: Does it wrap database logic?

### V. Usage Analysis (Who calls me?)
*   List top consumer forms/applications.
*   *Source*: Dependency Map (Upstream).

### VI. Modernization & Migration Notes
*   Map the Forms-specific pattern (e.g., "Global-based Modals") to its modern equivalent (e.g., "UI Component Library").
*   Identify complex logic needing Unit Tests.

## 3. Classification & Complexity
Rate the library complexity:
*   **Core (High)**: `JUSLIB`, `AGLIB`, `RCCLIB`. (Used system-wide, critical infrastructure).
*   **Domain (Medium)**: `RCC_LIB3`, `JRSLIB`. (Application specific logic).
*   **Utility (Low)**: `D2KWUTIL`. (Technical wrappers).

## 4. Quality Assurance
*   [ ] **API Completeness**: Are major procedures listed?
*   [ ] **State Check**: Are GLOBAL variable interactions documented?
*   [ ] **Linkage**: Are links to Overview files compliant with `enrich_links.py`?

## 5. Tooling
*   **Discovery**: `python plugins/cli.py bundle --target [LIB_NAME]` (Runs pll_miner)
*   **Enrichment**: `python scripts/documentation/enrich_links_v2.py`

## 6. Execution & Verification (MANDATORY)
To prevent "high-level" skipped steps, every library documentation task MUST include a granular per-phase Implementation Plan.

### Mandatory Task Lifecycle:
1.  **Draft Task**: Use `/maintenance-task` but manually expand the Implementation Plan into granular sub-steps (e.g., "Subtask 1.1: Context Bundle", "Subtask 1.2: Check for missing SQL dumps").
2.  **Intelligence Sync**: NO task is "Done" until the following are executed and verified:
    *   **RLM Distill**: `python plugins/rlm-factory/scripts/distiller.py --file [PATH]`
    *   **Vector Ingest**: `wsl python3 plugins/vector-db/scripts/ingest.py --file [PATH]` (for both Overview and any new Source artifacts).
    *   **Tracking Log**: `python scripts/documentation/update_analysis_tracking.py [ID]`
3.  **Verification**: The checklist must show `[x]` for all sub-steps before moving the file to `tasks/done/`.
