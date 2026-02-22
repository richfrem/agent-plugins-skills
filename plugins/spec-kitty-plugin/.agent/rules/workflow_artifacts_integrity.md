---
trigger: always_on
---

# Workflow Artifacts Integrity Policy

**Effective Date**: 2026-02-12
**Related Constitution Articles**: I (Hybrid Workflow), III (Zero Trust)

## Core Mandate: Tool-Generated Truth
The Agent MUST NOT simulate work or manually create process artifacts that are controlled by CLI tools.
**If a command exists to generate a file, YOU MUST USE IT.**

### 1. Spec Kitty Lifecycle
The following files are **READ-ONLY** for manual editing by the Agent. They MUST be generated/updated via CLI:

| Artifact | Mandatory Command | Forbidden Action |
|:---|:---|:---|
| `spec.md` | `/spec-kitty.specify` | Manually writing a spec file |
| `plan.md` | `/spec-kitty.plan` | Manually scaffolding a plan |
| `tasks.md` | `/spec-kitty.tasks` | Manually typing a task list |
| `tasks/WP-*.md` | `/spec-kitty.tasks` | Manually creating prompt files |
| Task lane changes | `.kittify/scripts/tasks/tasks_cli.py update` | Manually editing frontmatter or `[x]` |

**Violation**: Creating these files via `write_to_file` is a critical process failure.

### 2. Proof-Before-Trust (Anti-Simulation)
The Agent MUST NOT mark a checklist item as complete (`[x]`) unless:
1. The specific tool command for that step has been **actually executed** (not described).
2. The tool output has been **pasted into the conversation** as proof.
3. The artifact exists on disk (verified via verification tool or file read).

**Simulation is Lying**: Marking a task `[x]` based on "intent", "mental model", or narrating "I would now run..." is prohibited. The ONLY acceptable proof is real command output.

**Known agent failure modes**:
- Writing "Seal complete" without running `/sanctuary-seal`
- Narrating "I would now run the verification" instead of running it
- Skipping closure phases (seal/persist/retrospective) to "save time"
- Marking kanban tasks as done without using the tasks CLI

### 3. Kanban Sovereignty
- **NEVER** manually edit WP frontmatter (lane, agent, shell_pid fields)
- **ALWAYS** use `.kittify/scripts/tasks/tasks_cli.py` for lane transitions
- **ALWAYS** run `/spec-kitty.status` after a lane change and paste the board as proof
- **NEVER** mark a WP as `done` without first running verification tools

### 4. Closure Is Mandatory
When a session ends, the agent MUST execute the full closure sequence:
```
/sanctuary-seal → /sanctuary-persist → /sanctuary-retrospective → /sanctuary-end
```
Each step requires pasted output as proof. Skipping any step is a protocol violation.

### 5. Git Sovereignty (Human Gate)
- **NEVER** set `SafeToAutoRun: true` for `git push`.
- **NEVER** push directly to `main` (Protected Branch).
- **ALWAYS** use a feature branch (`feat/...`, `fix/...`, `docs/...`).
- **ALWAYS** wait for explicit user approval for any push.

### 6. Worktree Hygiene
- **Never** manually create directories inside `.worktrees/`.
- **Always** use `spec-kitty implement` (or `run_workflow.py`) to manage worktrees.
- **Cleanup**: Delete worktrees only via `git worktree remove` or approved cleanup scripts.
