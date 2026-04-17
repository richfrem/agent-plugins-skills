---
concept: command-template-spec-kittytasks-research-mission
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/tasks.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.370243+00:00
cluster: source
content_hash: 175eb381bc7a976f
---

# Command Template: /spec-kitty.tasks (Research Mission)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Generate research work packages with subtasks aligned to methodology phases.
---

# Command Template: /spec-kitty.tasks (Research Mission)

**Phase**: Design (finalizing work breakdown)
**Purpose**: Break research work into independently executable work packages with subtasks.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Location Pre-flight Check

Verify you are in the planning repository (not a worktree). Task generation happens on the target branch for ALL missions.

1. Run `spec-kitty agent feature check-prerequisites --json --paths-only --include-tasks` from the repository root and capture:
   - `target_branch` / `base_branch`
   - `TARGET_BRANCH` / `BASE_BRANCH`
   - `feature_dir`

   Treat this JSON as canonical branch context for this command. Do not infer from `meta.json`.

```bash
git branch --show-current  # Should match TARGET_BRANCH from check-prerequisites JSON
```

**Note**: Task generation in the target branch is standard for all spec-kitty missions. Implementation happens in per-WP worktrees.

---

## Outline

1. **Setup**: Use the `check-prerequisites` JSON from Location Pre-flight and capture:
   - `feature_dir`
   - `target_branch` / `base_branch`

   **CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).
   It also returns `runtime_vars.now_utc_iso` (`NOW_UTC_ISO`) for deterministic timestamp fields.

   **YOU MUST USE THIS PATH** for ALL subsequent file operations.

2. **Load design documents**:
   - spec.md (research question, scope, objectives)
   - plan.md (methodology, phases, quality criteria)
   - research.md (background, prior art)
   - data-model.md (entities, relationships)

3. **Derive fine-grained subtasks**:

   ### Subtask Patterns for Research

   **Literature Search & Source Collection** (Phase 1):
   - T001: Define search keywords and inclusion/exclusion criteria
   - T002: [P] Search academic database 1 (IEEE, PubMed, arXiv, etc.)
   - T003: [P] Search academic database 2
   - T004: [P] Search gray literature and industry sources
   - T005: Screen collected sources for relevance
   - T006: Populate source-register.csv with all candidate sources
   - T007: Prioritize sources by relevance rating

   **Source Review & Evidence Extraction** (Phase 2):
   - T010: [P] Review high-relevance sources (parallelizable by source)
   - T011: Extract key findings into evidence-log.csv
   - T012: Assign confidence levels to findings
   - T013: Document limitations and caveats
   - T014: Identify patterns/themes emerging from evidence

   **Analysis & Synthesis** (Phase 3):
   - T020: Code findings by theme/category
   - T021: Identify patterns across sources and confidence levels
   - T022: Assess strength of evidence supporting each claim
   - T023: Draw conclusions mapped to sub-questions
   - T024: Document limitations and threats to validity
   - T025: Write findings.md with synthesis and bibliography references

   **Quality & Validation** (Phase 4):
   - T030: Verify source coverage meets minimum requirements
   - T031: Validate evidence citations are traceable
   - T032: Check for bias in source selection
   - T033: Review methodology adherence
   - T034: External validation (if applicable)

4. **Roll subtasks into work packages**:

   ### Work Package Patterns for Research

   **Standard Research Flow**:
   - WP01: Literature Search & Source Collection (T001-T007)
   - WP02: Source Review & Evidence Extraction (T010-T014)
   - WP03: Analysis & Synthesis (T020-T025)
   - WP04: Quality Validation (T030-T034)

   **Empirical Research (if applicable)**:
   - WP01: Literature Review (background, prior art)
   - WP02: Study Design & Setup
   - WP03: Data Collection
   - WP04: Analysis & Findings
   - WP05: Quality Validation

   **Multi-Researcher Parallel**:
   - WP01: Search & Collect (foundation)
   - WP02a: [P] Source Revi

*(content truncated)*

## See Also

- [[command-template-spec-kittytasks-documentation-mission]]
- [[command-template-spec-kittyimplement-documentation-mission]]
- [[command-template-spec-kittyplan-documentation-mission]]
- [[command-template-spec-kittyreview-documentation-mission]]
- [[command-template-spec-kittyspecify-documentation-mission]]
- [[sources-template---research-topic-name]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/tasks.md`
- **Indexed:** 2026-04-17T06:42:10.370243+00:00
