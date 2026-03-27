# SOP: Codify Database Type

**Source Workflow**: `/codify-db-type`
**Target**: `legacy-system/oracle-db-overviews/types/[TypeName]-Type-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [TypeName] --type type`
- [ ] **Verify Context**: Check `temp/context-bundles/[TypeName]_context.md`.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/database-object-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (Data structure definition)
- [ ] **Fill Section**: **Attributes** (Fields)
- [ ] **Fill Section**: **Methods** (Member functions)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
