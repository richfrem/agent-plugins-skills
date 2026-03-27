# SOP: Codify Menu (MMB)

**Source Workflow**: `/codify-menu`
**Target**: `legacy-system/oracle-forms-overviews/menus/[MenuName]-Menu-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [MenuName] --type menu`
- [ ] **Verify Context**: Check `temp/context-bundles/[MenuName]_context.md` for hierarchy and roles.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/menu-overview-template.md` (if exists) or base structure to target path.
- [ ] **Fill Section**: **Purpose** (Main Menu vs Context)
- [ ] **Fill Section**: **Hierarchy** (Menu structure visualization)
- [ ] **Fill Section**: **Security** (Role restrictions)
- [ ] **Fill Section**: **Events** (PL/SQL logic)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
