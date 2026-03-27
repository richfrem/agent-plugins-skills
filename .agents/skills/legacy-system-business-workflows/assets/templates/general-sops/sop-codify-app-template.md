# SOP: Codify Application

**Source Workflow**: `/codify-app`
**Target**: `legacy-system/oracle-forms-overviews/apps/[AppName]-App-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [AppName] --type app`
- [ ] **Verify Context**: Check `temp/context-bundles/[AppName]_context.md`.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/application-overview-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (High level business function)
- [ ] **Fill Section**: **Modules** (List of Forms/Reports)
- [ ] **Fill Section**: **Architecture** (Tech stack, Diagram)
- [ ] **Fill Section**: **Navigation** (Menu structure reference)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
