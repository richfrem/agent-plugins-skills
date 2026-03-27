---
description: Complete Application overview documentation workflow.
inputs: [AppID]
tier: 3
---

**When to use:** Creation or update of an Application Overview to document high-level structure.

**This is an ORCHESTRATING workflow that uses these sub-commands in sequence:**

---

> **SYSTEM ENFORCEMENT PROTOCOL**
> 1. **MANDATORY EXECUTION**: You MUST invoke the `/legacy-system-oracle-forms_investigate-lineage` and `investigate-form` skills via the Skill tool.
> 2. **PROHIBITED ACTION**: Manual code reading, `grep`, or ad-hoc analysis is a VIOLATION.
> 3. **BLOCKING CONDITION**: If `temp/context-bundles/[AppID]_context.md` is not generated, you MUST NOT proceed to documentation.
> 4. **FAILURE MODE**: If the tool fails, STOP and report the error. Do not fallback to manual work.

## Phase 0: Pre-Flight (The Gate)

```bash
/agent-orchestrator_plan "codify-app-[AppID]"
```

**What this does:**
1.  **Context Check**: Verifies git branch and environment.
2.  **SDD Lifecycle**: Executes `/spec-kitty.specify` -> `/spec-kitty.plan` -> `/spec-kitty.tasks`.
3.  **Worktree Initialization**: Runs `spec-kitty implement WP-xx`.

> **⚠️ STOP:** Do not proceed to Phase 1 until the Orchestrator confirms the plan and tasks are generated.

---

## Phase 1: Knowledge Retrieval

### Step 1: Search Existing Context
*Check limits: Do not duplicate work if overview exists.*

---

## Phase 2: Analysis & Deep Dive

### Step 2: Menu Analysis (Subtask A)
```bash
/legacy-system-oracle-forms_investigate-menu [AppID]M0000
```
*(Assumes standard main menu naming e.g. RccM0000. If different, adjust.)*
*Extracts: Application structure, module grouping.*

### Step 3: Role Identification (Subtask C)
```bash
/legacy-system-roles_investigate-roles --app [AppID]
```
*(Or use `../skills/legacy-system-roles/scripts/split_roles.py` manually if bulk tool unavailable)*
*Check: roles_inventory.json for active vs legacy roles.*

### Step 4: Dependency Analysis (Subtask B)
```bash
/dependency-analysis_retrieve-dependency-graph [AppID]M0000 --downstream
```
*Identify core functional modules reachable from main menu.*

### Step 5: Fill Template
Populate `plugins/legacy system/assets/templates/general-sops/sop-codify-app-template.md` with findings.
Output to: `legacy-system/applications/[AppID]-Application-Overview.md`

---

## Phase 3: Intelligence Sync Pipeline (MANDATORY)
**Policy:** `plugins/legacy system/references/rules/documentation_granularity_policy.md`

### Step 6: Enrich Links
```bash
/legacy-system-oracle-forms_curate-enrich-links [OutputFile]
```

### Step 7: Distill to RLM

### Step 8: Ingest to Vector DB

### Step 9: Rebuild Master Collection
```bash
/inventory-manager_curate-inventories
```

---

## Universal Closure (MANDATORY)

### Step A: Retrospective
```bash
/agent-orchestrator_retro
```

### Step B: Finalize
```bash
/spec-kitty.merge
```

---

## ⚠️ Task Content Requirement
Every analysis task file MUST include a **"Review Items"** section following the **Implementation Plan**:
```markdown
## Review Items
- **Final Artifact**: [[AppID] Application Overview] (Reference Missing: [AppID]-Application-Overview.md)
```
// turbo-all
