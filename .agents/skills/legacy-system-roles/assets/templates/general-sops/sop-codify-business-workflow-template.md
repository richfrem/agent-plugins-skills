# SOP: Codify Business Workflow (BW)

**Source Workflow**: `/codify-business-workflow`
**Target**: `legacy-system/business-rules/BW-[ID]-[Name].md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [BW_ID] --type workflow` (if ID exists) or search.
- [ ] **Verify Context**: Check search results.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/business-rule-template.md` (Use BW section) to target path.
- [ ] **Fill Section**: **Steps** (Sequential user actions)
- [ ] **Fill Section**: **Roles** (Who performs this?)
- [ ] **Fill Section**: **Systems** (Apps involved)

## Phase 3: Intelligence Sync
- [ ] **BR Inventory**: `python scripts/inventory/business_rules_inventory_manager.py`
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
