# SOP: Codify Database View

**Source Workflow**: `/codify-db-view`
**Target**: `legacy-system/oracle-db-overviews/views/[ViewName]-View-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [ViewName] --type view`
- [ ] **Verify Context**: Check `temp/context-bundles/[ViewName]_context.md` for logic, base tables, and security.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/db-view-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (Business context)
- [ ] **Fill Section**: **Logic** (SQL query analysis)
- [ ] **Fill Section**: **Dependencies** (Base tables, functions)
- [ ] **Fill Section**: **App Security** (Row Level Security, Grants)
- [ ] **Fill Section**: **Callers** (Upstream forms/reports)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
