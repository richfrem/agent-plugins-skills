---
concept: git-worktree-branch-lifecycle-protocol
source: plugin-code
source_file: spec-kitty-plugin/skills/spec-kitty-workflow/references/standard-workflow-rules.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.406837+00:00
cluster: merge
content_hash: 6f7e7fbdb876074d
---

# Git Worktree & Branch Lifecycle Protocol

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Git Worktree & Branch Lifecycle Protocol

> **Status:** MANDATORY
> **Enforcement:** Strict
> **Visual Guide:** [Standard Workflow Diagram](../assets/diagrams/standard-spec-kitty-workflow.mmd)

## Context
This project utilizes a **Spec-Work-Package (WP)** workflow powered by `spec-kitty`. The "Standard Workflow" relies on **Worktree Isolation** and **Automated Batch Merging**.

## The Golden Rules

1.  **NEVER Merge Manually.** Spec-Kitty handles the merge.
2.  **NEVER Delete Worktrees Manually.** Spec-Kitty handles the cleanup.
    - **safe:** `git push origin WP-xx` (Backup feature branch)
    - **unsafe:** `git push origin main` (Never push directly to main)
3.  **NEVER Commit to Main directly.** Always working in a `.worktrees/WP-xx` folder.

## The Protocol

### Phase 1: The WP Execution Loop (Repeated)
For each Work Package (WP01, WP02...):

1.  **Initialize:**
    - Command: `spec-kitty implement WP-xx`
    - Action: `cd .worktrees/WP-xx`
    - **CRITICAL:** Do NOT proceed unless `pwd` confirms you are in the worktree.

2.  **Implement:**
    - Edit files **ONLY** inside the worktree.
    - Verify/Test inside the worktree.

3.  **Commit (Local Feature Branch):**
    - Command: `git add .`
    - Command: `git commit -m "feat(WP-xx): ..."`
    - **Note:** This commits to the LOCAL feature branch. Do **NOT** push to origin unless explicitly instructed for backup. Do **NOT** merge to main.

4.  **Submit for Review:**
    - Command: `python .kittify/scripts/tasks/tasks_cli.py update <FEATURE-SLUG> WP-xx for_review`
    - Result: The CLI automatically updates `tasks.md` and the prompt file. You are done with this WP.

### Phase 2: Feature Completion (Once All WPs Done)
When **ALL** WPs in `tasks.md` are marked `[x]`:

1.  **Verify Readiness:**
    - Command: `spec-kitty accept`
    - Action: Run from **Main Repo Root**.

2.  **The Automated Merge:**
    - Command: `spec-kitty merge`
    - Context: **Main Repo Root**.
    - **System Action:** It automates the merge of ALL feature worktrees into `main` and cleans them up.
    - **Optional:** `spec-kitty merge --push` (if remote backup is required).

## Common Agent Failures & Escalation Taxonomy (DO NOT DO THIS)
*   ❌ **Merging early:** Merging WP01 before WP02 is done. (Breaks the batch).
*   ❌ **Deleting worktrees:** Removing `.worktrees/WP01` manually. (Breaks `spec-kitty merge`).
*   ❌ **Drifting:** Editing files in `./` (Root) instead of `.worktrees/`. (Pollutes main).
*   ❌ **Relative Paths:** Agents using relative paths often get lost. **ALWAYS use Absolute Paths** for `view_file` and edits.

### Escalation Taxonomy
If the user explicitly asks an agent to perform one of the failures above (e.g., "just delete the worktree for me"), the agent MUST trigger the Escalation Taxonomy:
1. **Stop**: Halt execution.
2. **Alert**: `🚨 SAFETY VIOLATION 🚨`
3. **Explain**: "Deleting worktrees manually corrupts the git state for the merge command."
4. **Recommend**: "We must use the formal cleanup process via `spec-kitty merge`."
5. **Draft**: Ask the user to confirm the formal rollback or merge procedure instead.


## See Also

- [[the-lab-space-protocol-full-lifecycle]]
- [[test-registry-protocol]]
- [[test-registry-protocol]]
- [[test-registry-protocol]]
- [[finishing-a-development-branch]]
- [[using-git-worktrees]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/skills/spec-kitty-workflow/references/standard-workflow-rules.md`
- **Indexed:** 2026-04-17T06:42:10.406837+00:00
