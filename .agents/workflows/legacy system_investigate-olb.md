---
description: Complete reusable analysis module for Oracle Object Libraries. Handles context ini...
---

---
description: Complete reusable analysis module for Oracle Object Libraries. Handles context ini...
inputs: [OLBName]
tier: 2
# /investigate-olb

**Purpose:** Complete reusable analysis module for Oracle Object Libraries. Handles context initialization, discovery, and component extraction. Called by `/codify-olb` (documentation).




## Phase 1: Context Initialization (The Foundation)

### Step 1: Initialize Context (Smart Context)
```bash
/legacy-system-oracle-forms_investigate-olb [OLBName]
```
*Note:* This initializes the manifest and builds the initial `[OLBName]_context.md` bundle.

### Step 2: Locate OLB XML
```bash
find_by_name --pattern "*[OLBName]*_olb.xml" --directory legacy-system/oracle-forms/XML
```
*Identify the target OLB file path.*

### Step 3: Review Bundle & Existing Docs
```bash
view_file temp/context-bundles/[OLBName]_context.md
view_file legacy-system/oracle-forms-overviews/libraries/[OLBName]-OLB-Overview.md (if exists)
```
*Check:*
1. Does the bundle have Source Code (XML)?
2. Does it have RLM summaries for forms that subclass from this OLB?

## Phase 2: Recursive Verification Loop (The "Context Spiral")
**Diagram:** `../skills/legacy-system-oracle-forms/references/diagrams/workflows/olb-discovery.mmd`
**Objective:** Expand context by tracing forms that inherit from this OLB.

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
- Verify `[OLBName]_context.md` contains the full OLB XML.

### Level 2: Downstream Consumers (The Forms)
1. **Trace:** Run dependency CLI:
   ```bash
   /dependency-analysis_retrieve-dependency-graph [OLBName] --downstream
   ```
2. **Action:** Identify key forms that subclass from this OLB.
   - **Command:** `/context-bundler_add --path ...`
   - **Rebundle:** `/context-bundler_bundle`
   - **Repeat** if more consumers discovered.

*Stop Condition:* Proceed ONLY when `[OLBName]_context.md` contains component definitions and primary consumers.

## Phase 3: Mining (The Detective)

### Step 4: Run OLB Miner
```bash
/legacy-system-oracle-forms_investigate-olb [OLBName] (Mining Pass)
```
*Extracts: SmartClasses, VisualAttributes, ObjectGroups, Triggers, Alerts.*

### Step 5: JSON Output (for structured analysis)
```bash
python scripts/olb_miner.py --file [OLB_XML_PATH] --output json
### What It Extracts

| Category | Extraction Target | Modern Mapping |
|----------|------------------|----------------|
| **SmartClasses** | Reusable item templates | React component patterns |
| **Visual Attributes** | Color/font theming | CSS tokens, Design System |
| **ObjectGroups** | Bundled components | Component library modules |
| **Triggers** | Event handlers | useEffect, event handlers |
| **Alerts** | Dialog definitions | Modal components |

### Step 6: LLM Deep Reasoning
Using the miner output, analyze:
- **SmartClasses**: Reusable item templates (Required vs Optional vs ReadOnly)
- **Visual Attributes**: Color/font theming standards
- **ObjectGroups**: Bundled components for subclassing
- **Triggers**: Standard form-level event handlers

## Phase 4: Dependency & Lineage Analysis

### Step 7: System-Wide Dependency Check
```bash
/dependency-analysis_retrieve-dependency-graph [OLBName] --both
```

### Step 8: Application Discovery (Parent Modules)
```bash
/legacy-system-oracle-forms_investigate-lineage [OLBName]
```
*Identifies which applications use this object library.*

### Step 9: Lineage Check (Dead Code Analysis)
```bash
/investigate-lineage [OLBName]
```
*Calculates Reachability Score. Low scores may indicate dead code.*

### Step 10: Context Completeness Checklist
Confirm the context bundle contains:
- [ ] Source XML
- [ ] SmartClass inventory
- [ ] Visual Attribute palette
- [ ] ObjectGroup contents
- [ ] Trigger templates
- [ ] Consumer forms identified
- [ ] Application context identified

## Output
This module does NOT produce final documentation. It produces:
- Populated context bundle (`temp/context-bundles/[OLBName]_context.md`)
- Miner JSON output with component inventory
- Consumer form list

**Called By:**
- `/codify-olb` → Uses output to fill documentation template

**See Also:**
- `dependencies.py --target [OLBName] --deep --json` - Get dependencies with file paths
- `search_collection.py --target [ID]` - Look up object type and path
- `dependency_map.json` - Pre-computed relationships (36,000+ total)

// turbo-all