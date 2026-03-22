---
name: spec-kitty-implement
description: Create an isolated workspace (worktree) for implementing a specific work
---

## 🔗 Workflow Provenance

> **Source**: This skill augments the baseline workflow located at [`./workflows/spec-kitty.implement.md`](./workflows/spec-kitty.implement.md).
> It acts as an intelligent wrapper that is continuously improved with each execution.

## Constitution Context Bootstrap (required)

Before running workflow implement, load constitution context for this action:

```bash
spec-kitty constitution context --action implement --json
```

Use JSON `text` as governance context. On first load (`mode=bootstrap`), follow referenced docs as needed.

## ⚠️ CRITICAL: Working Directory Requirement

**After running `spec-kitty implement WP##`, you MUST:**

1. **Run the cd command shown in the output** - e.g., `cd .worktrees/###-feature-WP##/`
2. **ALL file operations happen in this directory** - Read, Write, Edit tools must target files in the workspace
3. **NEVER write deliverable files to the main repository** - This is a critical workflow error

**Why this matters:**
- Each WP has an isolated worktree with its own branch
- Changes in main repository will NOT be seen by reviewers looking at the WP worktree
- Writing to main instead of the workspace causes review failures and merge conflicts

## Deterministic Pre-Read Checks (required)

Before any `Read`/`Edit`/`Write` action, run these checks from your shell:

```bash
pwd
ls -la
test -f kitty-specs/<feature>/tasks/<wp-file>.md && echo "wp prompt exists"
```

If a file/path is uncertain, verify first with `ls` or `test -f` before reading it.

---

**IMPORTANT**: After running the command below, you'll see a LONG work package prompt (~1000+ lines).

**You MUST scroll to the BOTTOM** to see the completion command!

Resolve canonical action context first:

```bash
spec-kitty agent context resolve --action implement --agent <your-name> --json
```

Then run the returned `workflow` command to get the work package prompt and
implementation instructions.

<details><summary>PowerShell equivalent</summary>

```powershell
spec-kitty agent context resolve --action implement --agent <your-name> --json
```

</details>

**CRITICAL**: You MUST provide `--agent <your-name>` to track who is implementing!

The resolver returns the exact work package and base workspace command. Do not
guess the feature slug, work package, or `--base` value in the prompt.

If the workflow prompt indicates `review_status: "has_feedback"`, read the frontmatter `review_feedback` pointer first (`feedback://...`). That pointer is the canonical reviewer feedback artifact.

---

## Commit Workflow

**BEFORE moving to for_review**, you MUST commit your implementation:

```bash
cd .worktrees/###-feature-WP##/
# Stage only expected deliverables for this WP (never use `git add -A`)
git add <deliverable-path-1> <deliverable-path-2> ...
git commit -m "feat(WP##): <describe your implementation>"
```

<details><summary>PowerShell equivalent</summary>

```powershell
Set-Location .worktrees\###-feature-WP##\
# Stage only expected deliverables for this WP (never use `git add -A`)
git add <deliverable-path-1> <deliverable-path-2> ...
git commit -m "feat(WP##): <describe your implementation>"
```

</details>

**Then move to review:**
```bash
spec-kitty agent tasks move-task WP## --to for_review --note "Ready for review: <summary>"
```

**Why this matters:**
- `move-task` validates that your worktree has commits beyond main
- Uncommitted changes will block the move to for_review
- This prevents lost work and ensures reviewers see complete implementations

---

**The Python script handles all file updates automatically - no manual editing required!**

**NOTE**: If `/spec-kitty.status` shows your WP in "doing" after you moved it to "for_review", don't panic - a reviewer may have moved it back (changes requested), or there's a sync delay. Focus on your WP.

---

## 🚀 Supplemental Best Practices (Augmented)

### Worktree Discipline

- **Absolute Paths Only**: When editing files in a worktree, ALWAYS use absolute paths (e.g., `/Users/.../Project_Ecosystem/.worktrees/<FEATURE>-WP01/path/to/file.py`). NEVER use relative paths, as agents frequently drift into the wrong directory.
- **Verify Before Coding**: Before writing any code, confirm you're in the correct worktree (`pwd` and `git branch --show-current`). The branch name must match the WP you're implementing.
- **One WP Per Worktree**: Each WP has its own isolated worktree branch. NEVER write deliverable files to the main repo root! Changes in the main repository will NOT be seen by reviewers looking at the WP worktree.

### Commit Hygiene

- **Stage Only Deliverables**: Stage specific deliverables (`git add path/to/file.py`). NEVER use `git add -A` or `git add .` (this captures kitty-specs changes and .gitignore noise).
- **Commit Message Format**: Use `feat(WP##): <imperative description>`.
- **Before Moving to Review**: The `move-task` command validates that your worktree has commits beyond main, no uncommitted changes exist, and no kitty-specs artifacts leaked into your branch.
  - For uncommitted changes: `git commit` or `git checkout -- <file>`
  - For kitty-specs leakage (use `--force` only if content is valid): `python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE-SLUG> WP## for_review --force`

### Dependency Management

When a WP depends on another WP:
1. Check that the dependency WP is already merged to main.
2. If not merged, your worktree may be missing files — create your worktree off the dependency branch instead.
3. Document the dependency in the WP frontmatter.

### Known Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Files written to main instead of worktree | Agent used wrong cwd | Always verify with `pwd` before editing |
| `move-task` blocked by uncommitted changes | Forgot to commit or staged extra files | `git status` then commit or checkout |
| `move-task` blocked by kitty-specs artifacts | Serial implementation leaked status changes | Use `--force` if content is valid |
| Missing files from dependency WP | WP was created before dependency was merged | Rebase worktree onto main after dependency merges |
