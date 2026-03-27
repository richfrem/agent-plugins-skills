# SOP: Codify Business Rule (BR)

**Source Workflow**: `/codify-business-rule`
**Target**: `legacy-system/business-rules/BR-[ID]-[Name].md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [BR_ID] --type rule` (if ID exists) or search by keyword.
- [ ] **Verify Context**: Check `temp/context-bundles/...` or search results.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/business-rule-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (What logic is enforced?)
- [ ] **Fill Section**: **Logic** (Pseudocode/SQL)
- [ ] **Fill Section**: **Source** (Where is it implemented? Form/DB?)
- [ ] **Fill Section**: **Impact** (What happens if violated?)

## Phase 3: Intelligence Sync
- [ ] **BR Inventory**: `python scripts/inventory/business_rules_inventory_manager.py`
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
