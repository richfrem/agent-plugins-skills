# GitHub Ecosystem Phase 2 (Repository Operational Memory) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 2 of the GitHub Ecosystem: Repository Operational Memory (ROM) — including routing contracts across task skills, `github-issue-backlog-agent` bridge skill, `github-issue-prioritizer`, `issue-worktree-agent`, `issue-pr-lifecycle-agent`, `repository-improvement-agent`, and GitHub Projects v2 custom field integration.

**Status / Completed Substrate (Phase 1.5):**
- ✅ `gh_issue_close.py` (Issue resolution closure CLI)
- ✅ `friction_cluster_agent.py` (Friction hotspot clustering engine)
- ✅ `issue-resolution-reviewer.agent.md` (Post-closure quality audit sub-agent)

---

## Architectural Routing & Capability Boundaries

To prevent capability fragmentation and agent confusion, all task and issue skills enforce strict routing intelligence:

| Intent / Scope | Assigned Skill | Backlog Substrate | Lifetime |
| :--- | :--- | :--- | :--- |
| Single-session scratchpad | `task-agent` | Local `tasks/*.md` | Ephemeral (Session) |
| Friction, bug, & debt logging | `github-issue-agent` | GitHub Issues (`gh issue`) | Durable (Repository) |
| Promoting scratch task -> GitHub Issue | `github-issue-backlog-agent` | Bridge (`tasks/*.md` ↔ GitHub) | Transition |
| Ranking & Projects v2 Sync | `github-issue-prioritizer` | GitHub Projects v2 | Operational |
| Isolated git execution branch | `issue-worktree-agent` | Git worktree (`.worktrees/`) | Execution |
| Full Issue -> Worktree -> PR -> Close | `issue-pr-lifecycle-agent` | Git + GitHub PR | Workflow |
| Friction hotspot -> Refactor PR | `repository-improvement-agent` | Core Repository Source | Evolution |

---

## Remaining Implementation Tasks

### Task 1: Skill Routing Contracts & Purpose Alignment
Refactor `SKILL.md` and `evals/evals.json` across `task-agent` and `github-issue-agent` to enforce strict routing boundaries.

**Files:**
- Modify: `plugins/dev-utils/skills/task-agent/SKILL.md`
- Modify: `plugins/dev-utils/skills/github-issue-agent/SKILL.md`
- Modify: `plugins/dev-utils/skills/github-issue-agent/evals/evals.json`

- [ ] **Step 1: Update `task-agent/SKILL.md` with explicit ephemeral intra-session routing rule**
- [ ] **Step 2: Update `github-issue-agent/SKILL.md` with durable repository friction/bug logging rule**
- [ ] **Step 3: Update `evals.json` routing criteria for both skills**
- [ ] **Step 4: Commit changes to git**

---

### Task 2: Escalation Bridge Skill (`github-issue-backlog-agent`)
Scaffold `github-issue-backlog-agent` to bridge local `task-agent` scratch items (`tasks/*.md`) into durable GitHub Issues.

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-backlog-agent/SKILL.md`
- Create: `plugins/dev-utils/skills/github-issue-backlog-agent/evals/evals.json`
- Create: `plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py`
- Test: `plugins/dev-utils/skills/github-issue-backlog-agent/tests/test_task_to_issue_bridge.py`

- [ ] **Step 1: Write failing unit test for task-to-issue bridge**
- [ ] **Step 2: Implement `task_to_issue_bridge.py`**
- [ ] **Step 3: Create `SKILL.md` and `evals.json`**
- [ ] **Step 4: Commit changes to git**

---

### Task 3: Priority Ranking & Projects v2 Custom Field Sync (`github-issue-prioritizer`)
Build `github-issue-prioritizer` to automatically rank issues (P0-P3) based on friction tier, frequency, and blockages, synchronizing with GitHub Projects v2 custom fields.

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-prioritizer/SKILL.md`
- Create: `plugins/dev-utils/skills/github-issue-prioritizer/evals/evals.json`
- Create: `plugins/dev-utils/skills/github-issue-prioritizer/scripts/gh_issue_prioritize.py`
- Test: `plugins/dev-utils/skills/github-issue-prioritizer/tests/test_gh_issue_prioritize.py`

- [ ] **Step 1: Write failing unit test for priority calculation and field formatting**
- [ ] **Step 2: Implement `gh_issue_prioritize.py`**
- [ ] **Step 3: Create `SKILL.md` and `evals.json`**
- [ ] **Step 4: Commit changes to git**

---

### Task 4: Isolated Execution Worktree Skill (`issue-worktree-agent`)
Build `issue-worktree-agent` to create isolated git worktrees for specific issues before executing agent tasks.

**Files:**
- Create: `plugins/dev-utils/skills/issue-worktree-agent/SKILL.md`
- Create: `plugins/dev-utils/skills/issue-worktree-agent/evals/evals.json`
- Create: `plugins/dev-utils/skills/issue-worktree-agent/scripts/issue_worktree_manage.py`
- Test: `plugins/dev-utils/skills/issue-worktree-agent/tests/test_issue_worktree.py`

- [ ] **Step 1: Write failing unit test for worktree creation/cleanup**
- [ ] **Step 2: Implement `issue_worktree_manage.py`**
- [ ] **Step 3: Create `SKILL.md` and `evals.json`**
- [ ] **Step 4: Commit changes to git**

---

### Task 5: End-to-End Issue-PR Lifecycle Agent (`issue-pr-lifecycle-agent`)
Build `issue-pr-lifecycle-agent` to orchestrate the end-to-end flow: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.

**Files:**
- Create: `plugins/dev-utils/skills/issue-pr-lifecycle-agent/SKILL.md`
- Create: `plugins/dev-utils/skills/issue-pr-lifecycle-agent/evals/evals.json`
- Create: `plugins/dev-utils/skills/issue-pr-lifecycle-agent/scripts/issue_pr_orchestrate.py`
- Test: `plugins/dev-utils/skills/issue-pr-lifecycle-agent/tests/test_issue_pr_orchestrate.py`

- [ ] **Step 1: Write failing unit test for PR lifecycle orchestration**
- [ ] **Step 2: Implement `issue_pr_orchestrate.py`**
- [ ] **Step 3: Create `SKILL.md` and `evals.json`**
- [ ] **Step 4: Commit changes to git**

---

### Task 6: Repository Operational Memory Synthesis Engine (`repository-improvement-agent`)
Build `repository-improvement-agent` sub-agent in `agent-agentic-os` to consume `friction_cluster_agent` hotspot reports and automatically propose/implement systemic refactoring PRs.

**Files:**
- Create: `plugins/agent-agentic-os/agents/repository-improvement-agent.agent.md`
- Modify: `plugins/agent-agentic-os/rules/github-issue-logging-policy.md`

- [ ] **Step 1: Implement `repository-improvement-agent.agent.md`**
- [ ] **Step 2: Update Agentic OS logging policy to trigger repository-improvement-agent on Tier 3 hotspots**
- [ ] **Step 3: Commit changes to git**

---

### Task 7: Full Ecosystem Reinstall & Verification Pass
- [ ] **Step 1: Run complete unit test suite across all plugins**
- [ ] **Step 2: Run `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y`**
- [ ] **Step 3: Run `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose`**
- [ ] **Step 4: Run `python3 plugins/agent-scaffolders/scripts/update_ecosystem_index.py`**
