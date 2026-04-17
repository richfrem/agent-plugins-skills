---
concept: spec-kittyspecify---create-feature-specification
source: plugin-code
source_file: spec-kitty-plugin/workflows/spec-kitty.specify.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.413898+00:00
cluster: user
content_hash: 5a91625f86778e32
---

# /spec-kitty.specify - Create Feature Specification

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- spec-kitty-command-version: 3.0.3 -->
# /spec-kitty.specify - Create Feature Specification

**Version**: 0.11.0+

## 📍 WORKING DIRECTORY: Stay in the project root checkout

**IMPORTANT**: Specify works in the project root checkout. NO worktrees are created.

```bash
# Run from project root:
cd /path/to/project/root  # Your project root checkout

# All planning artifacts are created in the project root and committed:
# - kitty-specs/###-feature/spec.md → Created in project root
# - Committed to target branch (from create-feature JSON: target_branch/base_branch)
# - NO worktrees created
```

**Worktrees are created later** during `/spec-kitty.implement`, not during planning.

**In repos with multiple features, always pass `--feature <slug>` to every spec-kitty command.**

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Branch Strategy Confirmation (MANDATORY)

Before discovery, resolve branch intent through the Python helper, not by probing git directly:

```bash
spec-kitty agent feature branch-context --json
```

If the user already told you the intended landing branch, pass it explicitly:

```bash
spec-kitty agent feature branch-context --json --target-branch <intended-branch>
```

Parse the JSON and, in your next reply, explicitly tell the user:

- Current branch at workflow start: `current_branch`
- Default planning/base branch if you create the feature right now: `planning_base_branch`
- Final merge target for completed changes: `merge_target_branch`
- Whether `branch_matches_target` is true or false
- If that is not the intended landing branch, stop and ask which branch should receive this feature before you run `create-feature`

Never talk generically about `main` or "the default branch". Name the actual branch values from the helper JSON. Do not shell out to git for this prompt.

## DO NOT

- Do not mix functional, non-functional, and constraint requirements in one list.
- Do not emit requirements without stable IDs (`FR-###`, `NFR-###`, `C-###`).
- Do not leave requirement status fields empty.
- Do not write non-functional requirements without measurable thresholds.
- Do not proceed to planning with unresolved requirement quality checklist failures.

## Constitution Context Bootstrap (required)

Before discovery questions, load constitution context for this action:

```bash
spec-kitty constitution context --action specify --json
```

- If JSON `mode` is `bootstrap`, treat JSON `text` as the initial governance context and consult referenced docs as needed.
- If JSON `mode` is `compact`, proceed with concise governance context.

## Discovery Gate (mandatory)

Before running any scripts or writing to disk you **must** conduct a structured discovery interview.

- **Scope proportionality (CRITICAL)**: FIRST, gauge the inherent complexity of the request:
  - **Trivial/Test Features** (hello world, simple pages, proof-of-concept): Ask 1-2 questions maximum, then proceed. Examples: "a simple hello world page", "tic-tac-toe game", "basic contact form"
  - **Simple Features** (small UI additions, minor enhancements): Ask 2-3 questions covering purpose and basic constraints
  - **Complex Features** (new subsystems, integrations): Ask 3-5 questions covering goals, users, constraints, risks
  - **Platform/Critical Features** (authentication, payments, infrastructure): Full discovery with 5+ questions

- **User signals to reduce questioning**: If the user says "just testing", "quick prototype", "skip to next phase", "stop asking questions" - recognize this as a signal to minimize discovery and proceed with reasonable defaults.

- **First response rule**:
  - For TRIVIAL features (hello world, simple test): Ask ONE clarifying question, then if the answer confirms it's simple, proceed directly to spec generation
  - For other features: Ask a single focused discovery question and end with `WAITING_FOR_DISCOVERY_INPUT`

- If the user provides no initial description (e

*(content truncated)*

## See Also

- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittytasks-outline---create-task-breakdown-document]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/workflows/spec-kitty.specify.md`
- **Indexed:** 2026-04-17T06:42:10.413898+00:00
