# SOP: Codify Role

**Source Workflow**: `/codify-role`
**Target**: `legacy-system/reference-data/inventories/roles.json` (and individual role docs if applicable)

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [RoleName] --type role`
- [ ] **Verify Context**: Check `temp/context-bundles/[RoleName]_context.md` for usages.

## Phase 2: Documentation
- [ ] **Check Inventory**: Verify role exists in `roles.json`.
- [ ] **Document Usages**: Update role description with list of Forms/Menus where it is used.
- [ ] **Update Matrix**: If applicable, update the Role-Form matrix.

## Phase 3: Intelligence Sync
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
