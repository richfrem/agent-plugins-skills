# SOP: Codify Database Package

**Source Workflow**: `/codify-db-package`
**Target**: `legacy-system/oracle-db-overviews/packages/[PackageName]-Package-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [PackageName] --type package`
- [ ] **Verify Context**: Check `temp/context-bundles/[PackageName]_context.md` for procedures and functions.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/db-package-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (API Contract)
- [ ] **Fill Section**: **Public API** (Procedures/Functions exposed)
- [ ] **Fill Section**: **Private Logic** (Internal helpers)
- [ ] **Fill Section**: **State** (Global variables/Constants)
- [ ] **Fill Section**: **Dependencies** (Tables, Other Packages)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
