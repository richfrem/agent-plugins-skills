---
concept: spec-kittyplan---create-implementation-plan
source: plugin-code
source_file: spec-kitty-plugin/workflows/spec-kitty.plan.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.411864+00:00
cluster: user
content_hash: c28ef26081a0adaf
---

# /spec-kitty.plan - Create Implementation Plan

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- spec-kitty-command-version: 3.0.3 -->
# /spec-kitty.plan - Create Implementation Plan

**Version**: 0.11.0+

## 📍 WORKING DIRECTORY: Stay in the project root checkout

**IMPORTANT**: Plan works in the project root checkout. NO worktrees created.

```bash
# Run from project root (same directory as /spec-kitty.specify):
# You should already be here if you just ran /spec-kitty.specify

# Creates:
# - kitty-specs/###-feature/plan.md → In project root checkout
# - Commits to target branch
# - NO worktrees created
```

**Do NOT cd anywhere**. Stay in the project root checkout root.

**In repos with multiple features, always pass `--feature <slug>` to every spec-kitty command.**

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Branch Strategy Confirmation (MANDATORY)

Before asking planning questions or generating artifacts, you must make the branch contract explicit.

- Never describe the landing branch vaguely. Always name the actual branch value.
- If the user says the feature should land somewhere else, stop and resolve that before writing `plan.md`.
- You must repeat the branch contract twice during this command:
  1. immediately after parsing `setup-plan --json`
  2. again in the final report before suggesting `/spec-kitty.tasks`

## Constitution Context Bootstrap (required)

Before planning interrogation, load constitution context for this action:

```bash
spec-kitty constitution context --action plan --json
```

- If JSON `mode` is `bootstrap`, apply JSON `text` as first-run governance context and follow referenced docs as needed.
- If JSON `mode` is `compact`, continue with condensed governance context.

## Location Check (0.11.0+)

This command runs in the **project root checkout**, not in a worktree.

- Resolve branch context from deterministic JSON output, not from `meta.json` inspection:
  - Run `spec-kitty agent feature setup-plan --feature <feature-slug> --json`
  - Use `current_branch`, `target_branch` / `base_branch`, and `planning_base_branch` / `merge_target_branch` (plus uppercase aliases) from that payload
  - Use `branch_matches_target` from that payload to detect branch mismatch; do not probe branch state manually inside the prompt
- Planning artifacts live in `kitty-specs/###-feature/`
- The plan template is committed to the target branch after generation

**Path reference rule:** When you mention directories or files, provide either the absolute path or a path relative to the project root (for example, `kitty-specs/<feature>/tasks/`). Never refer to a folder by name alone.

## Planning Interrogation (mandatory)

Before executing any scripts or generating artifacts you must interrogate the specification and stakeholders.

- **Scope proportionality (CRITICAL)**: FIRST, assess the feature's complexity from the spec:
  - **Trivial/Test Features** (hello world, simple static pages, basic demos): Ask 1-2 questions maximum about tech stack preference, then proceed with sensible defaults
  - **Simple Features** (small components, minor API additions): Ask 2-3 questions about tech choices and constraints
  - **Complex Features** (new subsystems, multi-component features): Ask 3-5 questions covering architecture, NFRs, integrations
  - **Platform/Critical Features** (core infrastructure, security, payments): Full interrogation with 5+ questions

- **User signals to reduce questioning**: If the user says "use defaults", "just make it simple", "skip to implementation", "vanilla HTML/CSS/JS" - recognize these as signals to minimize planning questions and use standard approaches.

- **First response rule**:
  - For TRIVIAL features: Ask ONE tech stack question, then if answer is simple (e.g., "vanilla HTML"), proceed directly to plan generation
  - For other features: Ask a single architecture question and end with `WAITING_FOR_PLANNING_INPUT`

- If the user has not provided plan context, keep interrogating with one question at a time.

- **Conversation

*(content truncated)*

## See Also

- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittytasks-outline---create-task-breakdown-document]]
- [[spec-kittytasks-outline---create-task-breakdown-document]]
- [[spec-kittyspecify---create-research-specification]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/workflows/spec-kitty.plan.md`
- **Indexed:** 2026-04-17T06:42:10.411864+00:00
