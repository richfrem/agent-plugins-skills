---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Naming Conventions
- **Task ID**: T001, T002... (Sequential)
- **Story Label**: [US1], [US2]... (Mandatory for story tasks)
- **Parallel**: [P] (Optional, indicates no dependencies)

<!-- 
  ============================================================================
  TEMPLATE INSTRUCTIONS
  
  1. Setup & Foundations: ALWAYS include Phase 1 & 2.
  2. Story Execution: Create one Phase per User Story (P1 -> P2 -> P3).
  3. Closure: ALWAYS include the Final Phase (Retrospective/Merge).
  ============================================================================
-->

## Phase 0: Pre-Flight
- [ ] T000 Check for existing branch `spec/[NNN]-[name]`
- [ ] T001 If clean, create/checkout branch `spec/[NNN]-[name]`
- [ ] T002 Initialize Spec Bundle (`spec.md`, `plan.md`) via `/sanctuary-start`

## Phase 1: Setup
- [ ] T003 Initialize project/script structure
- [ ] T004 [P] Configure environment/dependencies

## Phase 2: Foundation (Blocking)
- [ ] T005 [Crucial step blocking all stories]

## Phase 3: User Story 1 (Priority: P1)
- [ ] T006 [US1] Implementation Step 1
- [ ] T007 [P] [US1] Implementation Step 2

## Phase 4: User Story 2 (Priority: P2)
- [ ] T008 [US2] Implementation Step 1

## Phase N: Closure & Merge (MANDATORY)
- [ ] TXXX Run `/sanctuary-retrospective` (Generates `retrospective.md`)
- [ ] TXXX Complete Retrospective with User (Part A questions)
- [ ] TXXX Agent completes Part B self-assessment
- [ ] TXXX Update key templates if issues found (e.g., `tasks-template.md`, `workflow-retrospective-template.md`)
- [ ] TXXX Run `/sanctuary-end` — This handles: Human Review Gate → Git Add/Commit/Push → PR Creation
- [ ] TXXX Wait for User to confirm: "PR Merged?"
- [ ] TXXX ONLY AFTER USER CONFIRMS MERGE: Run `/sanctuary-end` again for cleanup (branch deletion, task closure)
