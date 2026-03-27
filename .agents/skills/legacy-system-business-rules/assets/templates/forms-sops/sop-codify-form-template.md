# SOP: Codify Oracle Form

**Workflow Type**: `codify-form`
**Purpose**: Complete analysis and documentation of an Oracle Form (.fmb).

## Phase 0: Pre-Flight (Git & Context)
- [ ] T000 Check for existing branch `spec/[NNN]-[form_name]`
- [ ] T001 If clean, create/checkout branch
- [ ] T002 Initialize Spec Bundle (`spec.md`, `plan.md`) via `/workflow-start`

## Phase 1: Context & Analysis
- [ ] T003 Run `/investigate-form [FORM_NAME]` to gather raw data
- [ ] T004 Run `plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle` to generate RLM Knowledge Bundle
- [ ] T005 Verify RLM Bundle covers: Triggers, Blocks, Role Access

## Phase 2: Documentation (Drafting)
- [ ] T006 Create/Update `docs/overviews/forms/[FORM_NAME]-Overview.md`
- [ ] T007 Document "Validation Logic" (Field vs Form level)
- [ ] T008 Document "Navigation Flow" (Call_Form, Open_Form)
- [ ] T009 Document "Database Interactions" (Procedures/Packages used)

## Phase 3: Business Rule Extraction
- [ ] T010 Identify embedded Business Rules in PL/SQL
- [ ] T011 Run `/codify-business-rule` for each new Rule found
- [ ] T012 Link Rules back to Form Overview

## Phase 4: Verification
- [ ] T013 Run `enrich_links_v2.py` to fix markdown links
- [ ] T014 Run `update_analysis_tracking.py` to log progress

## Phase 5: Closure & Merge
- [ ] T015 Run `/workflow-retrospective`
- [ ] T016 Commit all changes (Overview + Rules + Analysis)
- [ ] T017 Push and Create PR
- [ ] T018 Confirm Merge
- [ ] T019 Run `/workflow-end`
