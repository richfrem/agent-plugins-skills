---
concept: command-template-spec-kittytasks-documentation-mission
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/tasks.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.333101+00:00
cluster: work
content_hash: 4ad732e30e840bbf
---

# Command Template: /spec-kitty.tasks (Documentation Mission)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Generate documentation work packages and subtasks aligned to Divio types.
---

# Command Template: /spec-kitty.tasks (Documentation Mission)

**Phase**: Design (finalizing work breakdown)
**Purpose**: Break documentation work into independently implementable work packages with subtasks.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Location Pre-flight Check

Verify you are in the primary repository checkout (not a worktree). Task generation happens on the feature target branch for all missions.

1. Run `spec-kitty agent feature check-prerequisites --json --paths-only --include-tasks` and capture:
   - `target_branch` / `base_branch`
   - `TARGET_BRANCH` / `BASE_BRANCH`
   - `feature_dir`

   Treat this JSON as the canonical branch contract for this command.

```bash
git branch --show-current  # Should match TARGET_BRANCH from check-prerequisites JSON
```

**Note**: Task generation happens on the feature target branch. Implementation happens later in per-WP worktrees.

---

## Outline

1. **Setup**: Use the pre-flight `check-prerequisites` JSON and keep `feature_dir` plus `target_branch/base_branch` in context.

2. **Load design documents**:
   - spec.md (documentation goals, selected Divio types)
   - plan.md (structure design, generator configs)
   - gap-analysis.md (if gap-filling mode)
   - meta.json (iteration_mode, generators_configured)

3. **Derive fine-grained subtasks**:

   ### Subtask Patterns for Documentation

   **Structure Setup** (all modes):
   - T001: Create `docs/` directory structure
   - T002: Create index.md landing page
   - T003: [P] Configure Sphinx (if Python detected)
   - T004: [P] Configure JSDoc (if JavaScript detected)
   - T005: [P] Configure rustdoc (if Rust detected)
   - T006: Set up build script (Makefile or build.sh)

   **Tutorial Creation** (if tutorial selected):
   - T010: Write "Getting Started" tutorial
   - T011: Write "Basic Usage" tutorial
   - T012: [P] Write "Advanced Topics" tutorial
   - T013: Add screenshots/examples to tutorials
   - T014: Test tutorials with fresh user

   **How-To Creation** (if how-to selected):
   - T020: Write "How to Deploy" guide
   - T021: Write "How to Configure" guide
   - T022: Write "How to Troubleshoot" guide
   - T023: [P] Write additional task-specific guides

   **Reference Generation** (if reference selected):
   - T030: Generate Python API reference (Sphinx autodoc)
   - T031: Generate JavaScript API reference (JSDoc)
   - T032: Generate Rust API reference (cargo doc)
   - T033: Write CLI reference (manual)
   - T034: Write configuration reference (manual)
   - T035: Integrate generated + manual reference
   - T036: Validate all public APIs documented

   **Explanation Creation** (if explanation selected):
   - T040: Write "Architecture Overview" explanation
   - T041: Write "Core Concepts" explanation
   - T042: Write "Design Decisions" explanation
   - T043: [P] Add diagrams illustrating concepts

   **Quality Validation** (all modes):
   - T050: Validate heading hierarchy
   - T051: Validate all images have alt text
   - T052: Check for broken internal links
   - T053: Check for broken external links
   - T054: Verify code examples work
   - T055: Check bias-free language
   - T056: Build documentation site
   - T057: Deploy to hosting (if applicable)

4. **Roll subtasks into work packages**:

   ### Work Package Patterns

   **For Initial Mode**:
   - WP01: Structure & Generator Setup (T001-T006)
   - WP02: Tutorial Documentation (T010-T014) - If tutorials selected
   - WP03: How-To Documentation (T020-T023) - If how-tos selected
   - WP04: Reference Documentation (T030-T036) - If reference selected
   - WP05: Explanation Documentation (T040-T043) - If explanation selected
   - WP06: Quality Validation (T050-T057)

   **For Gap-Filling Mode**:
   - WP01: High-Priority Gaps (tasks for critical missing docs from gap analysis)
   - WP02: Medium-Priority Ga

*(content truncated)*

## See Also

- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/tasks.md`
- **Indexed:** 2026-04-17T06:42:10.333101+00:00
