# SOP: Codify Database Trigger

**Source Workflow**: `/codify-db-trigger`
**Target**: `legacy-system/oracle-db-overviews/triggers/[TriggerName]-Trigger-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [TriggerName] --type trigger`
- [ ] **Verify Context**: Check `temp/context-bundles/[TriggerName]_context.md` for logic.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/db-trigger-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (Business logic/Validation)
- [ ] **Fill Section**: **Event** (BEFORE/AFTER INSERT/UPDATE)
- [ ] **Fill Section**: **Logic** (PL/SQL analysis)
- [ ] **Fill Section**: **Dependencies** (Tables, Sequences)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
