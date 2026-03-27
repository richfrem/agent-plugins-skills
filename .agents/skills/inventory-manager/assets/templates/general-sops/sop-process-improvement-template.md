# SOP: Process Improvement / Meta-Task

**Workflow Type**: `process`
**Purpose**: For tasks involving documentation, script updates, or process improvements (Track C or Meta-Work).

## Phase 0: Pre-Flight
- [ ] T000 Check for existing branch `spec/[NNN]-[name]`
- [ ] T001 If clean, create/checkout branch `spec/[NNN]-[name]`
- [ ] T002 Initialize Spec Bundle (`spec.md`, `plan.md`) via `/workflow-start`

## Phase 1: Analysis & Design
- [ ] T003 Analyze existing process/scripts to identify gaps
- [ ] T004 Design the new process flow or script logic
- [ ] T005 Update `plan.md` with technical approach (if complex)
- [ ] T006 Review Constitution for compliance (if changing policies)

## Phase 2: Implementation (Drafting)
- [ ] T007 [P] Create/Update templates or documentation files
- [ ] T008 [P] Create/Update scripts or tools
- [ ] T009 Verify file paths and naming conventions

## Phase 3: Verification (Meta-Test)
- [ ] T010 Run the new script/process in a "Dry Run" or Test mode
- [ ] T011 Verify output artifacts match expectations
- [ ] T012 Validate that no existing workflows are broken (Regression Test)

## Phase 4: Closure & Merge
- [ ] T013 Run `/workflow-retrospective` to capture process learnings
- [ ] T014 Commit all changes to Feature Branch
- [ ] T015 Push to remote and Create Pull Request
- [ ] T016 Confirm with User: "PR Merged?"
- [ ] T017 Run `/workflow-end` to cleanup local branch

