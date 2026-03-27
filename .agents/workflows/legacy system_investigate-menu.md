---
description: Complete reusable analysis module for Oracle Menus. Handles context initialization...
---

---
description: Complete reusable analysis module for Oracle Menus. Handles context initialization...
inputs: [MenuID]
tier: 2
# /investigate-menu

**Purpose:** Complete reusable analysis module for Oracle Menus. Handles context initialization, recursive discovery, and multi-pass mining. Called by `/codify-menu` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
/legacy-system-oracle-forms_investigate-menu [MenuID]
```
*Note:* This initializes the manifest and builds the initial `[MenuID]_context.md` bundle.

### Step 2: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[MenuID]_context.md
view_file legacy-system/oracle-forms-overviews/menus/[MenuID]-Menu-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (XML)?
2. Does it have RLM summaries for forms it navigates to?

## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Diagram:** `../skills/legacy-system-oracle-forms/references/diagrams/workflows/menu-discovery.mmd`
**Objective:** Recursively expand the context by tracing forms and roles.

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
### Level 1: Core Logic (The Source)
- Verify `[MenuID]_context.md` contains the full Menu XML section.

### Level 2: Downstream Targets (The Forms)
1. **Trace:** Run dependency CLI:
   ```bash
   /dependency-analysis_retrieve-dependency-graph [MenuID] --downstream
   ```
2. **Action:** Identify key forms launched by this menu.
   - **Command:** `/context-bundler_add --path ...`
   - **Rebundle:** `/context-bundler_bundle`
   - **Repeat** if more forms discovered.

### Level 3: Attached Libraries
1. **Trace:** Check for attached PLLs in menu:
   ```bash
   /legacy-system-database_investigate-code-search --target [MenuID] --query "AttachedLibrary"
   ```
2. **Action:** Add PLL source for shared logic.
   - **Command:** `/context-bundler_add --path ...`
   - **Rebundle:** `/context-bundler_bundle`

### Level 4: Role Security Context
   ```bash
   /legacy-system-oracle-forms_investigate-ui-menu [MenuID]
   ```

*Stop Condition:* Proceed ONLY when `[MenuID]_context.md` contains the hierarchy logic and its primary ecosystem.

## Phase 3: Multi-Pass Mining (The Detective)

### What It Extracts

| Category | Extraction Target | Description |
|----------|------------------|-------------|
| **Hierarchy** | Menu Modules, Sub-Menus | Top-level structure |
| **Commands** | CALL_FORM, OPEN_FORM, HOST | Navigation targets |
| **Roles** | Menu-level and Item-level restrictions | RBAC configuration |
| **Program Units** | Embedded PL/SQL | Menu logic |

### Pass 1: Hierarchy Tree (The Structure)
**Focus:** Menu Modules and Sub-Menus
```bash
/legacy-system-oracle-forms_investigate-menu [MenuID] (Mining Pass)
```

### Pass 2: Navigation & Commands (The Actions)
**Focus:** Menu Item Commands
```bash
/legacy-system-database_investigate-code-search --target [MenuID] --query "CALL_FORM|OPEN_FORM|NEW_FORM|HOST"
```
**Extracts:**
- Forms launched directly
- Operating system calls (HOST)
- PL/SQL blocks executed

### Pass 3: Role & Security Rules (The Gates)
**Focus:** Role-based visibility and enablement
```bash
/legacy-system-roles_investigate-form-roles [MenuID]
/legacy-system-database_investigate-code-search --target [MenuID] --query "SecureDisableItems|SET_MENU_ITEM_PROPERTY"
```
**Extracts:**
- Programmatic disables (`SET_MENU_ITEM_PROPERTY`)
- `SecureDisableItems` 

## Phase 4: Dependency & Lineage Analysis

### Step 6: System-Wide Dependency
```bash
/dependency-analysis_retrieve-dependency-graph [MenuID] --both
```

### Step 7: Application Discovery (Parent Modules)
```bash
/legacy-system-oracle-forms_investigate-lineage [MenuID]
```
*Identifies which applications this menu belongs to.*

### Step 8: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [MenuID]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

### Step 9: Security Verification
```bash
/legacy-system-roles_investigate-roles --app [MenuID]
```

### Step 10: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source XML
- [ ] Full hierarchy tree
- [ ] All navigation targets (forms)
- [ ] Attached Libraries (PLL)
- [ ] Role mappings verified
- [ ] Application context identified

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[MenuID]_context.md`)
- Console output with hierarchy and navigation patterns
- Security verification results

**Called By:**
- `/codify-menu` → Uses output to fill documentation template

**See Also:**
- `dependencies.py --target [MenuID] --deep --json` - Get dependencies with file paths
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ total)

// turbo-all