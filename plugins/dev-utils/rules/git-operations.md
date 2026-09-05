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
Before pushing any changes to GitHub or concluding updates to plugins or skills:
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

### 7. Commit only what is asked & required
- Commit only files within the task scope.
- Auto-modified files like `.DS_Store` or `uv.lock` should not be committed unless relevant.
- When `skills-lock.json` or `symlinks.json` changes as a direct result of adding/modifying skills or plugins, commit them together with the changes.

## Approval Required

- Any `git reset` (hard or soft)
- Any `git rebase -i`
- Any branch deletion (`git branch -d` / `-D`)
- Any `git push --force-with-lease` or force variant
- Any `git clean`

## Safe Without Asking

- `git status`, `git diff`, `git log` — read-only, always safe
- `git add <specific files>` + `git commit` when the user asked to commit
- `git push` (non-force) when the user asked to push
- Fetching and merging `origin/main` into the current working feature branch to keep PRs conflict-free
- `git checkout -b <branch>` when the user asks for a new branch

