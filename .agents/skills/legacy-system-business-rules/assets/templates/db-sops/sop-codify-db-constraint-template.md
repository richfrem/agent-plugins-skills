# SOP: Codify Database Constraint

**Source Workflow**: `/codify-db-constraint`
**Target**: `legacy-system/oracle-db-overviews/constraints/[ConstraintName]-Constraint-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [ConstraintName] --type constraint`
- [ ] **Verify Context**: Check `temp/context-bundles/[ConstraintName]_context.md`.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/db-constraint-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (Rule enforcing)
- [ ] **Fill Section**: **Definition** (SQL Definition)
- [ ] **Fill Section**: **Impact** (Table affected)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
