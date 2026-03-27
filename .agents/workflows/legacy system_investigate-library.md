---
description: Complete reusable analysis module for Oracle PL/SQL Libraries. Handles context ini...
---

---
description: Complete reusable analysis module for Oracle PL/SQL Libraries. Handles context ini...
tier: 2
inputs: [LibName]
# /investigate-library

**Purpose:** Complete reusable analysis module for Oracle PL/SQL Libraries. Handles context initialization, API mining, and dependency tracing. Called by `/codify-library` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
/legacy-system-oracle-forms_investigate-library [LibName]
```
*Note:* This initializes the manifest and builds the initial `[LibName]_context.md` bundle.

### Step 2: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[LibName]_context_bundle.md
view_file legacy-system/oracle-forms-overviews/libraries/[LibName]-Library-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (Markdown/PL/SQL)?
2. Does it have the Base Manifest loaded?

## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Diagram:** `../skills/legacy-system-oracle-forms/references/diagrams/workflows/library-discovery.mmd`
**Objective:** Expand context by tracing upstream consumers and downstream dependencies.

> **⚠️ CRITICAL: This is an ITERATIVE LOOP, not a one-shot process.**
> Repeat Steps until the context is complete.
>
> **Protocol:** See [context-spiral-protocol.md](../../docs/standards/context-spiral-protocol.md) for definitions.

```
┌─────────────────────────────────────────────────────────┐
│                    RECURSION LOOP                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Review  │───►│ Add File │───►│ Rebundle │───┐       │
│  │  Bundle  │◄───┴──────────┴────┴──────────┘   │       │
│  └────┬─────┘                                   │       │
│       │ Context Complete?                       │       │
│       ▼                                         │       │
│   [YES: Proceed to Mining]    [NO: Loop]────────┘       │
└─────────────────────────────────────────────────────────┘
### Level 1: Core Content (The Source)
- Verify `[LibName]_context_bundle.md` contains the full PLL source.

### Level 2: Downstream Verification
1. **Trace:** Run dependency CLI:
   ```bash
   /dependency-analysis_retrieve-dependency-graph [LibName] --downstream
   ```
2. **Action:** Identify any missing downstream dependencies (other libs/forms) and add them.
   - **Command:** `/context-bundler_add --path ...`
   - **Rebundle:** `/context-bundler_bundle`

### Level 3: Source Code Scan (Downstream)
1. **Trace:** Check code for manual calls:
   ```bash
   /legacy-system-database_investigate-code-search --target [LibName] --query "CALL_FORM|AttachedLibrary"
   ```
2. **Action:** Add downstream dependencies to manifest if missed by CLI.

### Level 4: Upstream Consumers (Who uses me?)
1. **Trace:**
   ```bash
   /dependency-analysis_retrieve-dependency-graph [LibName] --upstream
   ```
2. **Context:** Knowing the *callers* provides examples of how the API is used.
   - **Action:** If key consumers found: `/context-bundler_add --path ...`

*Stop Condition:* Proceed ONLY when context contains Source, Consumers, and key Dependencies.

## Phase 3: Mining (The Detective)

### Step 4: Run Library Miner (PLL Analysis)
```bash
/legacy-system-oracle-forms_investigate-library [LibName] (Mining Pass)
```
*Extracts: API Specification (Procedures/Functions), Global State Variables, Dependencies.*

### What It Extracts

| Category | Extraction Target | Modern Mapping |
|----------|------------------|----------------|
| **PublicAPI** | Procedures/Functions | Utility functions, Hooks |
| **GlobalState** | `GLOBAL.*` variables | Redux Slice / Context |
| **Dependencies** | DB Packages, Tables | API Services |
| **Complexity** | Lines of Code, Logic Depth | Refactoring difficulty |

## Phase 4: Dependency & Lineage Analysis

### Step 5: System-Wide Dependency Check
```bash
/dependency-analysis_retrieve-dependency-graph [LibName] --both
```

### Step 6: Application Discovery (Parent Modules)
```bash
/legacy-system-oracle-forms_investigate-lineage [LibName]
```
*Identifies which applications use this library.*

### Step 7: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [LibName]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

### Step 8: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source Code
- [ ] Public API list
- [ ] Global Variable usage
- [ ] Consumer list
- [ ] Application context identified

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[LibName]_context.md`)
- Console output with API and State analysis

**Called By:**
- `/codify-library` → Uses output to fill documentation template

**See Also:**
- `dependencies.py --target [LibName] --deep --json` - Get dependencies with file paths
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ total)

// turbo-all