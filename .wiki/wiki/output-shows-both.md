---
concept: output-shows-both
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/review.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.364600+00:00
cluster: review
content_hash: 8cf9ab98274472e0
---

# Output shows both:

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Perform structured research review with citation validation.
---

## Research Review Overview

Research WPs produce deliverables in a **worktree**, which merge to the target branch like code.

### Two Types of Artifacts

| Type | Location | Review Focus |
|------|----------|--------------|
| **Research Deliverables** | `{{deliverables_path}}` (in worktree) | PRIMARY - Your main review target |
| **Planning Artifacts** | `kitty-specs/{{feature_slug}}/research/` (in main) | SECONDARY - Citation validation only |

### Review Checklist

- [ ] Research deliverables exist in `{{deliverables_path}}/`
- [ ] Findings address the WP objectives
- [ ] Citations/sources are properly documented
- [ ] Deliverables are committed to worktree branch
- [ ] Quality meets research standards

---

## Understanding Research Dependencies

**For research missions, `dependencies: []` is often NORMAL.**

Research phases typically work like this:
- **Investigation phase**: WPs run in parallel, no inter-dependencies
- **Synthesis phase**: WPs depend on investigation WPs
- **Final/Validation phase**: Depends on synthesis

Empty dependencies means this WP CAN start immediately - it's **not an error**.

**To see dependency relationships:**
```bash
spec-kitty agent tasks list-dependents WP##

# Output shows both:
#   Depends on: (upstream - what blocks this WP)
#   Depended on by: (downstream - what this WP blocks)
```

**Why this matters for review:**
- If a WP has dependents and you request changes, those downstream WPs may need updates
- The review workflow will warn you about incomplete dependents

---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Location Pre-flight Check (CRITICAL for AI Agents)

Before proceeding with review, verify you are in the correct working directory by running the shared pre-flight validation:

```python
```

**What this validates**:
- Current branch follows the feature pattern like `001-feature-name`
- You're not attempting to run from `main` or any release branch
- The validator prints clear navigation instructions if you're outside the feature worktree

**Path reference rule:** When you mention directories or files, provide either the absolute path or a path relative to the project root (for example, `kitty-specs/<feature>/tasks/`). Never refer to a folder by name alone.

## Citation Validation (Research Mission Specific)

Before reviewing research tasks, validate all citations and sources:

```python
from pathlib import Path
from specify_cli.validators.research import validate_citations, validate_source_register

# Validate evidence log
evidence_log = FEATURE_DIR / "research" / "evidence-log.csv"
if evidence_log.exists():
    result = validate_citations(evidence_log)
    if result.has_errors:
        print(result.format_report())
        print("\nERROR: Citation validation failed. Fix errors before proceeding.")
        exit(1)
    elif result.warning_count > 0:
        print(result.format_report())
        print("\nWarnings found - consider addressing for better citation quality.")

# Validate source register
source_register = FEATURE_DIR / "research" / "source-register.csv"
if source_register.exists():
    result = validate_source_register(source_register)
    if result.has_errors:
        print(result.format_report())
        print("\nERROR: Source register validation failed.")
        exit(1)
```

**Validation Requirements**:
- All sources must be documented with unique `source_id` entries.
- Citations must be present in both CSVs (format warnings are advisory).
- Confidence levels should be filled for evidence entries.
- Research review cannot proceed if validation reports blocking errors.

## Outline

1. Run `{SCRIPT}` from repo root; capture `FEATURE_DIR`, `AVAILABLE_DOCS`, and `tasks.md` path.

2. Determine the review target:
   - If user input specifies a filename, validate it exists under `tasks/` (flat structure, check `lane: "fo

*(content truncated)*

## See Also

- [[output-templates]]
- [[pattern-action-forcing-output-with-deadline-attribution]]
- [[complexity-tiered-output-templating]]
- [[local-interactive-output-viewer-loop]]
- [[output-classification-tagging]]
- [[severity-stratified-output-schema-with-emoji-triage]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/review.md`
- **Indexed:** 2026-04-17T06:42:10.364600+00:00
