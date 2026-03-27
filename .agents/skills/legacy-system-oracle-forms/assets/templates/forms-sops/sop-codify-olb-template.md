# SOP: Codify Object Library (OLB)

**Source Workflow**: `/codify-olb`
**Target**: `legacy-system/oracle-forms-overviews/object-libraries/[LibraryName]-OLB-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [LibraryName] --type olb`
- [ ] **Verify Context**: Check `temp/context-bundles/[LibraryName]_context.md`.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/olb-overview-template.md` (if exists) or structure to target path.
- [ ] **Fill Section**: **Purpose** (Shared UI Components)
- [ ] **Fill Section**: **SmartClasses** (Reusable property sets)
- [ ] **Fill Section**: **Visual Attributes** (Colors/Fonts)
- [ ] **Fill Section**: **Usage** (Forms inheriting from this)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
