---
concept: stage-only-expected-deliverables-for-this-wp-never-use-git-add--a
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/software-dev/command-templates/implement.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.349003+00:00
cluster: work
content_hash: a86a8dd7d703b893
---

# Stage only expected deliverables for this WP (never use `git add -A`)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Create an isolated workspace (worktree) for implementing a specific work package.
---

## ⚠️ CRITICAL: Working Directory Requirement

**After running `spec-kitty implement WP##`, you MUST:**

1. **Run the cd command shown in the output** - e.g., `cd .worktrees/###-feature-WP##/`
2. **ALL file operations happen in this directory** - Read, Write, Edit tools must target files in the workspace
3. **NEVER write deliverable files to the main repository** - This is a critical workflow error

**Why this matters:**
- Each WP has an isolated worktree with its own branch
- Changes in main repository will NOT be seen by reviewers looking at the WP worktree
- Writing to main instead of the workspace causes review failures and merge conflicts

---

**IMPORTANT**: After running the command below, you'll see a LONG work package prompt (~1000+ lines).

**You MUST scroll to the BOTTOM** to see the completion command!

Run this command to get the work package prompt and implementation instructions:

```bash
spec-kitty agent workflow implement $ARGUMENTS --agent <your-name>
```

<details><summary>PowerShell equivalent</summary>

```powershell
spec-kitty agent workflow implement $ARGUMENTS --agent <your-name>
```

</details>

**CRITICAL**: You MUST provide `--agent <your-name>` to track who is implementing!

If no WP ID is provided, it will automatically find the first work package with `lane: "planned"` and move it to "doing" for you.

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


## See Also

- [[triple-loop-learning-system---architecture-overview]]
- [[agentic-os---future-vision]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[triple-loop-learning-system---architecture-overview]]
- [[finishing-a-development-branch]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/software-dev/command-templates/implement.md`
- **Indexed:** 2026-04-17T06:42:10.349003+00:00
