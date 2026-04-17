---
concept: command-template-spec-kittyplan-documentation-mission
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/plan.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.330896+00:00
cluster: docs
content_hash: 6936e43c65a7fd8a
---

# Command Template: /spec-kitty.plan (Documentation Mission)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Produce a documentation mission plan with audit/design guidance and generator setup.
---

# Command Template: /spec-kitty.plan (Documentation Mission)

**Phases**: Audit (if gap-filling), Design
**Purpose**: Plan documentation structure, configure generators, prioritize gaps, design content outline.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Location Pre-flight Check

Verify you are in the primary repository checkout (not a worktree). Planning happens on the feature target branch for all missions.

1. Run `spec-kitty agent feature setup-plan --json` and capture:
   - `target_branch` / `base_branch`
   - `TARGET_BRANCH` / `BASE_BRANCH`
   - `feature_dir`

   Treat this JSON as the canonical branch contract.

```bash
git branch --show-current  # Should match TARGET_BRANCH from setup-plan output
```

**Note**: Planning runs on the feature target branch. Implementation happens later in per-WP worktrees.

---

## Planning Interrogation

For documentation missions, planning interrogation is lighter than software-dev:
- **Simple projects** (single language, initial docs): 1-2 questions about structure preferences
- **Complex projects** (multiple languages, existing docs): 2-3 questions about integration approach

**Key Planning Questions**:

**Q1: Documentation Framework**
"Do you have a preferred documentation framework/generator?"
- Sphinx (Python ecosystem standard)
- MkDocs (Markdown-focused, simple)
- Docusaurus (React-based, modern)
- Jekyll (GitHub Pages native)
- None (plain Markdown)

**Why it matters**: Determines build system, theming options, hosting compatibility.

**Q2: Generator Integration Approach** (if multiple languages detected)
"How should API reference for different languages be organized?"
- Unified (all APIs in one reference section)
- Separated (language-specific reference sections)
- Parallel (side-by-side comparison)

**Why it matters**: Affects directory structure, navigation design.

---

## Outline

1. **Setup**: Use the pre-flight `setup-plan --json` output to initialize plan.md and keep `target_branch/base_branch` in context.

2. **Load context**: Read spec.md, meta.json (especially `documentation_state`)

3. **Phase 0: Research** (if gap-filling mode)

   ### Gap Analysis (gap-filling mode only)

   **Objective**: Audit existing documentation and identify gaps.

   **Steps**:
   1. Scan existing `docs/` directory (or wherever docs live)
   2. Detect documentation framework (Sphinx, MkDocs, Jekyll, etc.)
   3. For each markdown file:
      - Parse frontmatter for `type` field
      - Apply content heuristics if no explicit type
      - Classify as tutorial/how-to/reference/explanation or "unclassified"
   4. Build coverage matrix:
      - Rows: Project areas/features
      - Columns: Divio types (tutorial, how-to, reference, explanation)
      - Cells: Documentation files (or empty if missing)
   5. Calculate coverage percentage
   6. Prioritize gaps:
      - **High**: Missing tutorials (blocks new users)
      - **High**: Missing reference for public APIs
      - **Medium**: Missing how-tos for common tasks
      - **Low**: Missing explanations (nice-to-have)
   7. Generate `gap-analysis.md` with:
      - Current documentation inventory
      - Coverage matrix (markdown table)
      - Prioritized gap list
      - Recommendations

   **Output**: `gap-analysis.md` file in feature directory

   ---

   ### Generator Research (all modes)

   **Objective**: Research generator configuration options for detected languages.

   **For Each Detected Language**:

   **JavaScript/TypeScript → JSDoc/TypeDoc**:
   - Check if JSDoc installed: `npx jsdoc --version`
   - Research config options: output format (HTML/Markdown), template (docdash, clean-jsdoc)
   - Determine source directories to document
   - Plan integration with manual docs

   **Python → Sphinx**:
   - Check if Sphinx installed: `sphinx-build --version`
   - Rese

*(content truncated)*

## See Also

- [[command-template-spec-kittyimplement-documentation-mission]]
- [[command-template-spec-kittyreview-documentation-mission]]
- [[command-template-spec-kittyspecify-documentation-mission]]
- [[command-template-spec-kittytasks-documentation-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/plan.md`
- **Indexed:** 2026-04-17T06:42:10.330896+00:00
