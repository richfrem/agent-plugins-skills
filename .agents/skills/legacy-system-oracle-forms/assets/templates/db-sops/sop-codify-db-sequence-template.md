# SOP: Codify Database Sequence

**Source Workflow**: `/codify-db-sequence`
**Target**: `legacy-system/oracle-db-overviews/sequences/[SequenceName]-Sequence-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [SequenceName] --type sequence`
- [ ] **Verify Context**: Check `temp/context-bundles/[SequenceName]_context.md`.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/database-object-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (What entity does it serve?)
- [ ] **Fill Section**: **Configuration** (Start, Increment, Cache)
- [ ] **Fill Section**: **Consumers** (Triggers, Procedures)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
