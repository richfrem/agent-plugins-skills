# SOP: Codify Database Table

**Source Workflow**: `/codify-db-table`
**Target**: `legacy-system/oracle-db-overviews/tables/[TableName]-Table-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [TableName] --type table`
- [ ] **Verify Context**: Check `temp/context-bundles/[TableName]_context.md` for schemas, constraints, and indexes.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/db-table-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (Business context)
- [ ] **Fill Section**: **Columns** (Data types, Nullability, Comments)
- [ ] **Fill Section**: **Constraints** (PK, FK, Check, Unique)
- [ ] **Fill Section**: **Indexes** (Performance structures)
- [ ] **Fill Section**: **Triggers** (Attached logic logic)
- [ ] **Fill Section**: **Callers** (Upstream dependencies)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
