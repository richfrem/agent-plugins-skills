---
description: Rules for safe git operations — what requires explicit approval, what is forbidden, and how to handle push & lockfile conflicts.
globs: ["**/*"]
---

# Git Operations Policy

## Hard Rules (never violate)

### 1. No git stash without explicit instruction
Never run `git stash`, `git stash pop`, or `git stash apply` unless the user explicitly says to.
**Reason:** Stashing risks applying stale edits onto new branches and causing silent regressions.

### 2. Lockfile Conflict Protocol (`skills-lock.json`)
`skills-lock.json` contains machine-generated timestamps. When a branch or PR has conflicts in `skills-lock.json`:
- **NEVER** edit conflict markers by hand (`<<<<<<<`, `=======`, `>>>>>>>`).
- **NEVER** leave a PR in conflict state after pushing.
- **ALWAYS** resolve immediately via:
  ```bash
  git checkout --ours skills-lock.json
  python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y
  git add skills-lock.json
  ```

### 3. Pre-Push Freshness & Quality Gate
Before **explicitly pushing** changes to GitHub (i.e., only when the user has issued a direct push command):
1. **Upstream Freshness Check**: Verify the branch is up to date with `origin/main`:
   ```bash
   git fetch origin main
   git merge origin/main
   ```
   If `skills-lock.json` conflicts occur, apply Rule 2 immediately.

2. **Pre-Push Quality Audits (Mandatory)**:
   Run standard compliance, coding conventions, and structural audits on all modified plugins and skills from the repository root:
   - **Workspace Coding Conventions Audit**:
     ```bash
     python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py
     ```
   - **Compliance Audit**:
     ```bash
     python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/<plugin-name>
     ```
   - **Structural Audit**:
     ```bash
     python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
     ```
   - **Cross-Platform Symlink Check**:
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
   *Resolution Action:* If errors, missing references, or broken symlinks are reported, resolve them before committing or pushing. Never push with broken symlinks or failing convention audits.

3. **Verify Clean Working Tree**: Verify working directory is clean (`git status`) and push with `-u origin <branch>`.

### 4. When a push is rejected
If `git push` is rejected because the remote is ahead:
1. Run `git fetch origin` and `git merge origin/<branch>` or `git pull --rebase` (no stash).
2. If conflicts occur in `skills-lock.json`, resolve via Rule 2.
3. Push once clean. Never force-push around a rejected push.

### 5. No force push to main/master
Never `git push --force` to main or master under any circumstances.

### 6. No --no-verify
Never skip hooks with `--no-verify` unless the user explicitly requests it.

### 7. No autonomous PR or remote operations
- **Never run `gh pr create`**, `gh pr merge`, or any GitHub CLI command that creates or merges a pull request without an explicit, isolated user directive (e.g., "open a PR", "create a pull request now").
- Discussing, reviewing, or mentioning a PR in conversation does NOT constitute permission to open one.
- Applies equally to `hub`, `gh`, and any git alias that results in a remote-side PR or branch creation.

### 8. No branch switching during active unreviewed work
- Do not `git checkout`, `git switch`, or `git checkout -b` away from a feature branch that contains local commits not yet approved by the user.
- If a new branch is needed while work-in-progress commits exist on the current branch, stop and confirm with the user what to do with those commits before switching.

### 9. Commit only what is asked & required
- Commit only files within the task scope.
- Auto-modified files like `.DS_Store` or `uv.lock` should not be committed unless relevant.
- When `skills-lock.json` or `symlinks.json` changes as a direct result of adding/modifying skills or plugins, commit them together with the changes.

### 10. Evolution Integrity Gate — update map-debt BEFORE committing core logic
Any commit that touches files under `plugins/`, `src/`, or `py_services/` **must** do one of the following before `git commit`:
- Stage an update to `references/map-debt.md` recording the debt entry (RESOLVED or OPEN) for the change, **OR**
- Stage an update to `references/evolution-log.md` if one exists, **OR**
- Include `Evolution-Check: none` in the commit message body with a one-line justification.

**Failure mode this prevents:** committing core logic changes and only discovering the missing map-debt entry when CI fails on the PR — forcing a follow-up commit and a broken CI run.

**Correct sequence:**
1. Make code changes
2. Update `references/map-debt.md` (add or resolve the relevant DEBT entry)
3. `git add <code files> references/map-debt.md`
4. `git commit`

The CI gate (`Verify Evolution & Map Debt Compliance`) enforces this post-hoc. The rule enforces it pre-emptively. Both must be respected.

## Approval Required

- Any `git reset` (hard or soft)
- Any `git rebase -i`
- Any branch deletion (`git branch -d` / `-D`)
- Any `git push --force-with-lease` or force variant
- Any `git clean`

## Safe Without Asking

- `git status`, `git diff`, `git log` — read-only, always safe
- `git add <specific files>` + `git commit` when the user asked to commit
- `git push` (non-force) **only** when the user issued an explicit, isolated push directive (e.g., "push this branch", "push now") — conversational mentions of PRs or branches do NOT qualify
- Fetching and merging `origin/main` into the current working feature branch to keep it current — **but only while on that feature branch, and only if no local unreviewed commits would be lost or detached**
- `git checkout -b <branch>` when the user asks for a new branch **and no unreviewed local commits are present on the current branch**

