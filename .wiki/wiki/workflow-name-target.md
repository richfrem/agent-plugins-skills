---
concept: workflow-name-target
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/std_workflow_definition.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.750592+00:00
cluster: phase
content_hash: dd0d31d3cb795d66
---

# /workflow-name [Target]

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# /workflow-name [Target]

**Purpose:** [Brief description of what this workflow enables.]

> **Hybrid Workflow Compliance:**
> This workflow adheres to the Agent Workflow Orchestration Design.
> It MUST NOT proceed to execution without a valid `spec.md`, `plan.md`, and `tasks.md`.

---

## Phase 0: Pre-Flight (The Gate)

```bash
# MUST use the Shell Shim to enforce constitutional gates
spec-kitty agent feature create-feature "[WorkflowName]-[Target]" --json
```

**What this does:**
1.  **Context Check**: Verifies git branch and environment.
2.  **Spec Check**:
    - Checks for `kitty-specs/[ID]-[Target]/spec.md`.
    - **IF MISSING**: Orchestrator STOPS and prompts: *"No Spec found. Please run `/spec-kitty.specify` first."*
    - **IF PRESENT**: Validates `plan.md` and `tasks.md` exist.

> **⚠️ STOP:** Do not proceed to Phase 1 until `/workflow-start` returns SUCCESS.

---

## Phase 1: Analysis (Investigation)

### Step 1: Initialize Context
```bash
/investigate-[module] [Target]
```
*Gathers context, runs miners, and builds the bundle.*

### Step 2: Verify Context
```bash
view_file temp/context-bundles/[Target]_context.md
```
*Agent must confirm the bundle contains sufficient information to proceed.*

---

## Phase 2: Documentation (The Scribe)
*Only reachable if Phase 0 and Phase 1 are complete.*

### Step 3: Progressive Elaboration Check
**Constraint**: Do not blindly overwrite.
1.  Check if `[Target]-Overview.md` already exists.
2.  If yes, read it first to preserve "Human Overrides".

### Step 4: Write/Update Artifact
Using `[Module]-template.md`:
- Fill all sections.
- Link to Source Code.
- Link to `spec.md` (Traceability).

---

## Phase 3: Intelligence Sync (Mandatory)

### Step 5: Curate & Publish
```bash
/curate-enrich-links [OutputFile]
/codify-rlm-distill [OutputFile]
/curate-update-inventory
```

---

## Phase 4: Closure

### Step 6: Retrospective
```bash
/workflow-retrospective
```

### Step 7: Finalize
```bash
/spec-kitty.merge "docs: [WorkflowName] [Target]" tasks/in-progress/[TaskFile]
```


## See Also

- [[project-name]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[metrics-workflow-health-continuous-improvement]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/std_workflow_definition.md`
- **Indexed:** 2026-04-17T06:42:09.750592+00:00
