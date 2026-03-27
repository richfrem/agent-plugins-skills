# SOP: Codify Database Procedure

**Source Workflow**: `/codify-db-procedure`
**Target**: `legacy-system/oracle-db-overviews/procedures/[ProcedureName]-Procedure-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [ProcedureName] --type procedure`
- [ ] **Verify Context**: Check `temp/context-bundles/[ProcedureName]_context.md` for parameters and logic.

## Phase 1.5: Business Rule Reconciliation (Mandatory)
- [ ] **Check Candidates**: Look for `RAISE_APPLICATION_ERROR` in context bundle.
- [ ] **Search Existing**: `python plugins/legacy system/legacy-system-database/skills/legacy-system-database/scripts/search_plsql.py "[Keyword]"`
- [ ] **Register New**: `python plugins/legacy system/inventory-manager/skills/inventory-manager/scripts/business_rules_inventory_manager.py --source [ProcedureName] --description "..."`

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/db-procedure-template.md` to target path.
- [ ] **Fill Section**: **Purpose** (Action description)
- [ ] **Fill Section**: **Parameters** (IN/OUT/INOUT)
- [ ] **Fill Section**: **Logic** (Flow/Validation)
- [ ] **Fill Section**: **Dependencies** (Tables)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
