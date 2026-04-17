---
concept: spec-kittyspecify---create-research-specification
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/specify.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.369176+00:00
cluster: planning
content_hash: 551e27c2353eb0a5
---

# /spec-kitty.specify - Create Research Specification

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Create or update the research specification from a natural language research question.
---

# /spec-kitty.specify - Create Research Specification

**Version**: 0.11.0+

## 📍 WORKING DIRECTORY: Stay in planning repository

**IMPORTANT**: Specify works in the planning repository. NO worktrees are created.

```bash
# Run from project root:
cd /path/to/project/root  # Your planning repository

# All planning artifacts are created in the planning repo and committed:
# - kitty-specs/###-feature/spec.md → Created in planning repo
# - Committed to target branch (from create-feature JSON: target_branch/base_branch)
# - NO worktrees created
```

**Worktrees are created later** during `/spec-kitty.implement`, not during planning.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Discovery Gate (mandatory)

Before running any scripts or writing to disk you **must** conduct a structured discovery interview.

### Research-Specific Discovery Questions

For research missions, focus on:

1. **Research Question**: What is the primary question you want to answer?
2. **Research Type**: Literature review, empirical study, case study, competitive analysis?
3. **Scope**: What's in scope and out of scope for this research?
4. **Deliverables**: What outputs do you expect? (Report, analysis, recommendations, data)
5. **Audience**: Who will consume this research? (Technical, business, academic)

### Scope Proportionality (CRITICAL)

- **Simple Research** (quick analysis, single-source review): Ask 2-3 questions, then proceed
- **Standard Research** (multi-source analysis, comparative study): Ask 3-5 questions
- **Complex Research** (systematic review, multi-method study): Full discovery with 5+ questions

### Discovery Requirements

1. Maintain a **Discovery Questions** table internally. Do **not** render to user.
2. When you have sufficient context, paraphrase into an **Intent Summary** and confirm.
3. If user explicitly asks to skip questions, acknowledge and proceed with minimal discovery.

## Research Deliverables Location (CRITICAL)

**IMPORTANT**: Research missions have TWO types of artifacts:

| Type | Location | Purpose |
|------|----------|---------|
| **Planning Artifacts** | `kitty-specs/###/research/` | Evidence/sources for PLANNING this sprint |
| **Research Deliverables** | `deliverables_path` | Actual research OUTPUT (your work product) |

### Determining deliverables_path

During discovery, you MUST ask:

> "Where should I store the research outputs (reports, analysis, findings)?
>
> Recommended: `docs/research/<feature-name>/`
>
> Other options:
> - `research-outputs/<feature-name>/`
> - `docs/<feature-name>/`
> - Custom path (must NOT be inside `kitty-specs/`)"

**Default**: If user doesn't specify, use `docs/research/<feature-slug>/`

**Validation Rules**:
- Must NOT be inside `kitty-specs/` (reserved for planning artifacts)
- Must NOT be just `research/` at root (ambiguous)
- Should include feature name/slug for clarity

## Workflow (0.11.0+)

**Planning happens in the planning repository - NO worktree created!**

1. Creates `kitty-specs/###-feature/spec.md` directly in planning repo
2. Creates `kitty-specs/###-feature/meta.json` with `deliverables_path`
3. Automatically commits to target branch
4. No worktree created during specify

**Worktrees created later**: Use `spec-kitty implement WP##` to create a workspace for each work package.

## Location

- Work in: **Planning repository** (not a worktree)
- Creates: `kitty-specs/###-feature/spec.md`
- Commits to: target branch (from `create-feature --json` → `target_branch`)

## Outline

### 0. Generate a Research Title

- Summarize the research question into a short, descriptive title (≤7 words)
- Use the confirmed title to derive the kebab-case feature slug

### 1. Discovery Phase

- Conduct discovery interview (scaled to complexity)
- Determine deliverables_path (ask user or use default)
- Confirm Inten

*(content truncated)*

## See Also

- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/specify.md`
- **Indexed:** 2026-04-17T06:42:10.369176+00:00
