# SOP: Codify Database Function

**Workflow Type**: `codify-db-function`
**Purpose**: Analysis and documentation of a stored PL/SQL Function.

## Phase 0: Pre-Flight
- [ ] T000 Check/Create Branch `spec/[NNN]-[func_name]`
- [ ] T001 Initialize Spec Bundle

## Phase 1: Context & Analysis
- [ ] T002 Run `/investigate-db-function [FUNC_NAME]`
- [ ] T003 Generate Context Bundle (CLI)
- [ ] T004 Identify Inputs, Outputs, and Return Type

## Phase 2: Documentation
- [ ] T005 Create `docs/overviews/db-objects/functions/[FUNC_NAME].md`
- [ ] T006 Document "Dependencies" (Tables/Views accessed)
- [ ] T007 Document "Callers" (Forms/Packages that use this)
- [ ] T008 Extract Core Logic/Algorithm description

## Phase 3: Verification
- [ ] T009 Run `enrich_links_v2.py`
- [ ] T010 Update Inventory

## Phase 4: Closure & Merge
- [ ] T011 Run `/workflow-retrospective`
- [ ] T012 Commit & Push
- [ ] T013 Create PR & Confirm Merge
- [ ] T014 Run `/workflow-end`
