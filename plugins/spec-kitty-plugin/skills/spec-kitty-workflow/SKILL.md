---
name: Spec Kitty Workflow
description: Standard operating procedures for the Spec Kitty agentic workflow (Plan -> Implement -> Review -> Merge).
---

# Spec Kitty Workflow

Standard lifecycle for implementing features using Spec Kitty.

## CRITICAL: Anti-Simulation Rules

> **YOU MUST ACTUALLY RUN EVERY COMMAND LISTED BELOW.**
> Describing what you "would do", summarizing expected output, or marking
> a step complete without pasting real tool output is a **PROTOCOL VIOLATION**.
>
> **Proof = pasted command output.** No output = not done.

### Known Agent Failure Modes (DO NOT DO THESE)
1. **Checkbox theater**: Marking `[x]` without running the command or verification tool
2. **Manual file creation**: Writing spec.md/plan.md/tasks.md by hand instead of using CLI
3. **Kanban neglect**: Not updating task lanes, so dashboard shows stale state
4. **Verification skip**: Marking a phase complete without running `verify_workflow_state.py`
5. **Closure amnesia**: Finishing code but skipping review/merge/closure steps

---

## 0. Mandatory Planning Phase (Do NOT Skip)

Before implementing any code, you MUST generate artifacts using the CLI.
**Manual creation of `spec.md`, `plan.md`, or `tasks/` files is STRICTLY FORBIDDEN.**

### Step 0a: Specify
```bash
/spec-kitty.specify
```
**PROOF**: Paste output confirming spec.md was generated.

Then verify:
```bash
python3 plugins/spec-kitty/scripts/verify_workflow_state.py --feature <SLUG> --phase specify
```
**PROOF**: Paste the verification output showing the checkmark.
**STOP**: Do NOT proceed to Plan until verification passes.

### Step 0b: Plan
```bash
/spec-kitty.plan
```
**PROOF**: Paste output confirming plan.md was generated.

Then verify:
```bash
python3 plugins/spec-kitty/scripts/verify_workflow_state.py --feature <SLUG> --phase plan
```
**PROOF**: Paste the verification output.
**STOP**: Do NOT proceed to Tasks until verification passes.

### Step 0c: Tasks
```bash
/spec-kitty.tasks
```
**PROOF**: Paste output confirming tasks.md and WP files were generated.

Then verify:
```bash
python3 plugins/spec-kitty/scripts/verify_workflow_state.py --feature <SLUG> --phase tasks
```
**PROOF**: Paste the verification output.
**STOP**: Do NOT proceed to Implementation until verification passes.

---

## 1. Start a Work Package (WP)

### Step 1a: Create worktree
```bash
spec-kitty agent workflow implement --task-id <WP-ID> --agent "<AGENT-NAME>"
```
**PROOF**: Paste the output. Extract the worktree path from it.

If output is truncated or unclear:
```bash
git worktree list
```
**CRITICAL**: Do NOT guess the path. Verify it exists before proceeding.

### Step 1b: Update kanban
```bash
python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE> <WP-ID> doing \
  --agent "<AGENT-NAME>" --note "Starting implementation"
```
**PROOF**: Paste the CLI output confirming lane change.

Then verify the board:
```bash
/spec-kitty.status
```
**PROOF**: Paste the kanban board. Confirm your WP shows in "doing" lane.
**STOP**: Do NOT start coding until the kanban shows the WP in "doing".

---

## 2. Implementation Loop

1. **Navigate**: `cd .worktrees/<WP-ID>` — verify with `pwd`
2. **Setup**: Install dependencies if needed
3. **Code**: Implement the feature
4. **Test**: Run tests or manual verification
5. **Commit**: `git add . && git commit -m "feat(<WP>): description"` (local worktree)

---

## 3. Review & Handover

### Pre-Review Checklist (verify ALL before proceeding)
- [ ] All files committed in worktree (`git status` shows clean)
- [ ] Worktree path confirmed (`pwd` matches `.worktrees/<WP-ID>`)
- [ ] WP lane is `doing` (not already `for_review` or `done`)
- [ ] No untracked files that should be committed

### Step 3a: Verify clean state
```bash
python3 plugins/spec-kitty/scripts/verify_workflow_state.py --wp <WP-ID> --phase review
```
**PROOF**: Paste the output. Must show "Worktree is clean".
**STOP**: Do NOT proceed if there are uncommitted changes.

### Step 3b: Update kanban to for_review
```bash
python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE> <WP-ID> for_review \
  --agent "<AGENT-NAME>" --note "Implementation complete, ready for review"
```
**PROOF**: Paste the CLI output.

### Step 3c: Verify kanban updated
```bash
/spec-kitty.status
```
**PROOF**: Paste the board. WP must show in "for_review" lane.

### Step 3d: Sync specs in main repo
```bash
cd <PROJECT_ROOT>
git add kitty-specs
git commit -m "docs(specs): mark <WP-ID> complete"
```

---

## 4. Deterministic Closure Protocol

> **CRITICAL**: Every step below is MANDATORY. Skipping any step is a protocol violation.
> The closure chain is: **Review → Accept → Retrospective → Merge → Verify → Intel Sync**

### Step 4a: Review each WP
```bash
spec-kitty agent workflow review --task-id <WP-ID>
```
**PROOF**: Paste the review output. WP must move to `done` lane.

Repeat for each WP. Verify all WPs are in `done` lane:
```bash
/spec-kitty.status
```
**PROOF**: Paste the board. ALL WPs must show in "done" lane before proceeding.

### Step 4b: Accept feature
```bash
cd <PROJECT_ROOT>
spec-kitty accept --mode local --feature <SLUG>
```
**PROOF**: Paste the JSON output showing `summary.ok: true`.

> **Known Issue**: Accept may fail with "missing shell_pid in WP frontmatter".
> **Fix**: Add `shell_pid: N/A` to the WP frontmatter, or use `--lenient` flag:
> ```bash
> spec-kitty accept --mode local --feature <SLUG> --lenient
> ```

**STOP**: Do NOT proceed if accept fails. Resolve all outstanding issues first.

### Step 4c: Retrospective (MANDATORY)
```bash
/spec-kitty_retrospective
```
**PROOF**: Paste confirmation that `kitty-specs/<SPEC-ID>/retrospective.md` was created/updated.

> **This step is NOT optional.** Every feature closure MUST include a retrospective.
> The retrospective file MUST exist in `kitty-specs/<SPEC-ID>/` before merge.

### Step 4d: Pre-merge safety check
```bash
cd <PROJECT_ROOT>
git status
git worktree list
spec-kitty merge --feature <SLUG> --dry-run
```
**PROOF**: Paste all three outputs. Verify:
- [ ] You are in the **main repo root** (NOT inside a worktree)
- [ ] `git status` shows clean working tree
- [ ] Dry-run shows no conflicts

### Step 4e: Merge from main repo
```bash
cd <PROJECT_ROOT>
spec-kitty merge --feature <SLUG>
```

> **LOCATION RULE**: ALWAYS run merge from the **main repository root**.
> NEVER `cd` into a worktree to merge. The `@require_main_repo` decorator
> will block execution from worktrees.

If merge fails mid-way:
```bash
spec-kitty merge --feature <SLUG> --resume
```
**PROOF**: Paste the merge output showing success.

### Step 4f: Post-merge verification
```bash
git log --oneline -5
git worktree list
git branch
git status
```
**PROOF**: Paste all outputs. Verify:
- [ ] Merge commit(s) visible in log
- [ ] No orphaned worktrees remain for this feature
- [ ] WP branches have been deleted
- [ ] Working tree is clean

### Step 4g: Intelligence sync
```bash
python3 plugins/rlm-factory/scripts/distill.py --path kitty-specs/<SPEC-ID>/
```
**PROOF**: Paste output confirming RLM cache updated.

> If vector DB is available, also run:
> ```bash
> python3 plugins/vector-db/scripts/ingest.py --path kitty-specs/<SPEC-ID>/
> ```

### Step 4h: Update kanban to done
```bash
python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE> <WP-ID> done \
  --agent "<AGENT-NAME>" --note "Merged and cleaned up"
```
**PROOF**: Paste CLI output + final `/spec-kitty.status` board.

---

## Known Back-End Failure Modes

| Failure | Root Cause | Fix |
|:--------|:-----------|:----|
| Merge blocked by `@require_main_repo` | Agent ran merge from inside a worktree | `cd <PROJECT_ROOT>` first, then `spec-kitty merge --feature <SLUG>` |
| Accept fails with "missing shell_pid" | WP frontmatter missing `shell_pid` field | Add `shell_pid: N/A` to frontmatter, or use `--lenient` |
| Orphaned worktrees after merge | Merge failed mid-cleanup | `git worktree remove .worktrees/<WP-FOLDER>` then `git branch -d <WP-BRANCH>` |
| Lost data during merge | Agent merged from worktree instead of main repo | Always use `--feature <SLUG>` flag from project root |
| Retrospective skipped | Agent treated it as optional | Retrospective file must exist before merge is allowed |
| No closure state recorded | No post-merge verification step | Run Step 4f verification checklist |

---

## 5. Dual-Loop Mode (Protocol 133)

When Spec Kitty runs inside a Dual-Loop session, roles are split:

| Step | Who | Action |
|------|-----|--------|
| Specify/Plan/Tasks | **Outer Loop** (Antigravity) | Generates all artifacts |
| Implement | **Outer Loop** creates worktree, then **Inner Loop** (Claude) codes | Inner Loop receives Strategy Packet |
| Review/Merge | **Outer Loop** | Verifies output, commits, merges |

**Inner Loop constraints**:
- No git commands — Outer Loop owns version control
- Scope limited to the Strategy Packet — no exploratory changes
- If worktree is inaccessible, may implement on feature branch (fallback — log in friction log)

**Cross-reference**: [dual-loop-supervisor SKILL](../dual-loop-supervisor/SKILL.md) | [Protocol 133 workflow](../../workflows/sanctuary_protocols/dual-loop-learning.md)

---

## 6. Task Management CLI

The tasks CLI manages WP lane transitions. **Always use this instead of manually editing frontmatter or checkboxes.**

```bash
# List WPs and their lanes
python3 .kittify/scripts/tasks/tasks_cli.py list <FEATURE-SLUG>

# Move a WP between lanes (planned → doing → for_review → done)
python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE-SLUG> <WP-ID> <LANE> \
  --agent "<AGENT-NAME>" --note "reason"

# Append activity log entry without changing lane
python3 .kittify/scripts/tasks/tasks_cli.py history <FEATURE-SLUG> <WP-ID> \
  --note "what happened" --agent "<AGENT-NAME>"

# Roll back to previous lane
python3 .kittify/scripts/tasks/tasks_cli.py rollback <FEATURE-SLUG> <WP-ID>

# Check feature acceptance readiness
python3 .kittify/scripts/tasks/tasks_cli.py status --feature <FEATURE-SLUG>
```

**Valid lanes**: `planned`, `doing`, `for_review`, `done`

**Dashboard**: `/spec-kitty.dashboard` reads lane data from WP frontmatter.

---

## Common Issues

- **"Base workspace not found"**: WP depends on a merged WP. Create worktree off `main`:
  ```bash
  git worktree add .worktrees/<WP-FOLDER> main
  cd .worktrees/<WP-FOLDER>
  git checkout -b <WP-BRANCH-NAME>
  ```
- **"Already on main"**: Merge commands must run from project root, not inside a worktree.
- **Kanban not updating**: Verify you're using the CLI, not manually editing frontmatter.
