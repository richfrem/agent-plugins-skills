# SOP: Codify Library (PLL)

**Source Workflow**: `/codify-library`
**Target**: `legacy-system/oracle-forms-overviews/libraries/[LibraryName]-Library-Overview.md`

## Phase 1: Analysis
- [ ] **Run Investigation**: `python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py init --target [LibraryName] --type lib`
- [ ] **Verify Context**: Check `temp/context-bundles/[LibraryName]_context.md` for `pll_miner` output.

## Phase 2: Documentation
- [ ] **Initialize**: Copy `plugins/legacy system/templates/library-overview-template.md` (or general application template if none specific) to target path.
- [ ] **Fill Section**: **Purpose** (General Utilities vs Domain Logic)
- [ ] **Fill Section**: **API Specification** (Table of Procedures/Functions)
- [ ] **Fill Section**: **Global State** (Variables read/set)
- [ ] **Fill Section**: **Usage** (Who calls me?)

## Phase 3: Intelligence Sync
- [ ] **Enrich Links**: `/curate-enrich-links [TargetFile]`
- [ ] **RLM Distill**: `/codify-rlm-distill [TargetFile]`
- [ ] **Vector Ingest**: `/codify-vector-ingest [TargetFile]`
- [ ] **Inventory Update**: `/curate-update-inventory`

## Phase 4: Closure
- [ ] **Retrospective**: `/workflow-retrospective`
- [ ] **End Workflow**: `/workflow-end`
