---
concept: context-spiral-protocol
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/context-spiral-protocol.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.747548+00:00
cluster: dependencies
content_hash: 6d69e3e10e20116b
---

# Context Spiral Protocol

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Context Spiral Protocol
**Version:** 1.0 (PROPOSED)

## 1. Objective
Ensure comprehensive, non-destructive analysis of legacy Oracle Forms by recursively expanding the context boundary until all dependencies (Forms, Libraries, DB Objects) are identified and captured.

## 2. The Spiral Pattern
Analysis proceeds in concentric circles ("Spirals") starting from the Target Object.

### Level 1: Core Identity (The Target)
- **Source:** XML/Markdown of the form itself.
- **Miners:**
  - `XML_Miner` (Blocks, Items, Triggers)
  - `MMB_Miner` (Menu Structure - if Menu)
  - `PLL_Miner` (API Contract - if Library)
  - `OLB_Miner` (SmartClasses - if Object Library)

### Level 2: Direct Dependencies (The Neighbors)
- **Forms:** `CALL_FORM`, `OPEN_FORM` targets.
- **Libraries:** Attached `.pll` files.
- **Menus:** Referenced Menu Module.
- **Database:** Directly called Packages/Procedures (e.g. `PKG.PROC`).

### Level 3: Extended Lineage (The Neighborhood)
- **Downstream:** What do the neighbors call? (e.g., Library A calls Form B).
- **Upstream:** Who calls me? (Reverse dependency check).
  - *Critical for Libraries*: Know your consumers.

### Level 4: Deep Database (The Foundation)
- Tables/Views accessed via Packages.
- Row-Level Security (RLS) policies.
- Database Triggers on affected tables.

## 3. Completeness Checklist ("Stop Condition")
A Context Bundle is strictly **INCOMPLETE** until:

- [ ] **Files**: 100% of detected dependencies have a file entry in the bundle (or a placeholder note if missing from repo).
- [ ] **Roles**: All Hardcoded Roles (`'JAS_ADMIN'`) are cross-referenced with `roles_inventory.json`.
- [ ] **Logic**: All "Unknown PL/SQL" blocks are resolved via `miners` or `search`.
- [ ] **Menus**: If a Form has a specific menu, that Menu's structure is included.

## 4. Automation Contract
Tools (internal `scripts/` modules, `investigate-*.py`) must:
1.  **Detect Gaps**: Automatically flag missing dependencies.
2.  **Auto-Expand**: Attempt to resolve paths using `master_object_collection.json`.
3.  **Halt on Error**: Do not produce final documentation if the Spiral is broken (missing core dependencies).


## See Also

- [[rsvp-reading-protocol-referencennput-deep-context-here-so-it-is-not-loaded-into-context-implicitly]]
- [[context-folder-patterns]]
- [[context-status-specification-contextstatusmd]]
- [[test-registry-protocol]]
- [[quick-start-zero-context-guide]]
- [[the-lab-space-protocol-full-lifecycle]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/context-spiral-protocol.md`
- **Indexed:** 2026-04-17T06:42:09.747548+00:00
