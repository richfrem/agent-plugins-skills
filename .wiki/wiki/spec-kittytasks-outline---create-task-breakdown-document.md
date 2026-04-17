---
concept: spec-kittytasks-outline---create-task-breakdown-document
source: plugin-code
source_file: spec-kitty-plugin/workflows/spec-kitty.tasks-outline.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.414896+00:00
cluster: work
content_hash: ade38bf2bf98712d
---

# /spec-kitty.tasks-outline - Create Task Breakdown Document

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- spec-kitty-command-version: 3.0.3 -->
# /spec-kitty.tasks-outline - Create Task Breakdown Document

**Version**: 0.12.0+

## Purpose

Create `tasks.md` — the task breakdown document that defines work packages,
subtask lists, dependency descriptions, and sizing estimates. This step
produces the **outline only**; individual WP prompt files are generated in
the next step.

## ⚠️ CRITICAL: THIS IS THE MOST IMPORTANT PLANNING WORK

**You are creating the blueprint for implementation**. The quality of work packages determines:
- How easily agents can implement the feature
- How parallelizable the work is
- How reviewable the code will be
- Whether the feature succeeds or fails

**QUALITY OVER SPEED**: Take your time to understand the full scope deeply,
break work into clear pieces, and write detailed guidance.

---

## 📍 WORKING DIRECTORY: Stay in the project root checkout

**IMPORTANT**: This step works in the project root checkout. NO worktrees created.

**Do NOT cd anywhere**. Stay in the project root checkout root.

**In repos with multiple features, always pass `--feature <slug>` to every spec-kitty command.**

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Context Resolution

Before proceeding, resolve canonical command context:

```bash
spec-kitty agent context resolve --action tasks_outline --json
```

Treat that JSON as canonical for feature slug, feature directory, and target branch.
Do not probe git branch state manually inside the prompt.

## Steps

### 1. Setup

Run the exact `check_prerequisites` command returned by the resolver. Capture
`feature_dir` plus `available_docs`. All paths must be absolute.

**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path. **YOU MUST USE THIS PATH** for ALL subsequent file operations.

### 2. Load Design Documents

Read from `feature_dir` (only those present):
- **Required**: plan.md (tech architecture, stack), spec.md (user stories & priorities)
- **Optional**: data-model.md (entities), contracts/ (API schemas), research.md (decisions), quickstart.md (validation scenarios)

Scale your effort to the feature: simple UI tweaks deserve lighter coverage, multi-system releases require deeper decomposition.

### 3. Derive Fine-Grained Subtasks

Create complete list of subtasks with IDs `T001`, `T002`, etc.:
- Parse plan/spec to enumerate concrete implementation steps, tests (only if explicitly requested), migrations, and operational work.
- Capture prerequisites, dependencies, and parallelizability markers (`[P]` means safe to parallelize per file/concern).
- Assign IDs sequentially in execution order.
- **Ideal granularity**: One clear action (e.g., "Create user model", "Add login endpoint")

### 4. Roll Subtasks into Work Packages

Group subtasks into work packages (IDs `WP01`, `WP02`, ...):

**TARGET SIZE**: 3-7 subtasks per WP (200-500 line prompts)
**MAXIMUM**: 10 subtasks per WP (700 line prompts)
**If more than 10 subtasks needed**: Create additional WPs, don't pack them in

**GROUPING PRINCIPLES**:
- Each WP should be independently implementable
- Root in a single user story or cohesive subsystem
- Ensure every subtask appears in exactly one work package
- Name with succinct goal (e.g., "User Story 1 – Real-time chat happy path")
- Record metadata: priority, success criteria, risks, dependencies, included subtasks, and requirement references
- Every WP must include a `Requirement Refs` line listing IDs from `spec.md` (FR/NFR/C)

### 5. Write `tasks.md`

Write to `feature_dir/tasks.md` following the tasks template structure below (**do NOT write instructions to read a template file from `.kittify/`**):
- Populate Work Package sections (setup, foundational, per-story, polish) with `WPxx` entries
- Under each work package include:
  - Summary (goal, priority, independent test)
  - Requirement references (`Requirement Refs: FR-001, NFR-001, C-001`)
  - Included subtasks (checkbox list referenc

*(content truncated)*

## See Also

- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittytasks---generate-work-packages]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/workflows/spec-kitty.tasks-outline.md`
- **Indexed:** 2026-04-17T06:42:10.414896+00:00
