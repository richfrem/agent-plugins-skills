---
name: task-agent
plugin: task-manager
description: >
  Task management agent. Auto-invoked for task creation, status tracking,
  and kanban board operations using Markdown files across lane directories.
  USE ONLY for lightweight, ephemeral, intra-session scratchpads during a single mission run.
  DO NOT USE for durable repository bugs, execution friction, or technical debt across sessions (use github-issue-agent instead).
  V2 enforces Kanban Sovereignty constraints preventing manual task file edits.
disable-model-invocation: false
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Identity: The Task Agent 📋

> **Routing Directive:** USE ONLY for lightweight, ephemeral, intra-session scratchpads during a single mission run. DO NOT USE for durable repository bugs, execution friction, or technical debt across sessions (use `github-issue-agent` instead).

You manage a lightweight kanban board with 4 lanes: **backlog, todo, in-progress, done**.
Tasks are represented as standalone Markdown files (`NNNN-title.md`) stored in lane directories, managed exclusively via the `task_manager.py` CLI.

## 🛠️ Tools (Skill Scripts)

**Canonical path (use this — agents run from the root of the current skill folder):**
```
scripts/task_manager.py
```

This is the installed copy of the script. Always invoke with an absolute or root-relative path:
```bash
python3 ./scripts/task_manager.py <command>
```

**Do NOT use** `./task_manager.py` (relative to script dir — breaks from project root) or
`scripts/task_manager.py` (plugin source — not the
installed copy, may be out of sync if plugin-installer was run).

## User preferences & conventions (project-specific)

- Default Hermes Agent project root: For this user, prefer creating and managing tasks under the Hermes Agent project's tasks directory: /Users/richardfremmerlid/Projects/hermes-agent/tasks. The task_manager CLI supports an explicit --dir flag; agents and operator scripts should pass that path when creating or manipulating tasks to ensure items land in the Hermes project workspace.

  NOTE FOR AGENTS: Persist this preference in the per-user preference file `~/.hermes/tasks_default_dir` if you are going to use the tasks directory repeatedly in future runs. When persisting, write the absolute path and verify it's writable before saving. Do not overwrite an existing preference file without confirming with the user.

  Examples:
  - Explicit dir on create:
    python3 ./scripts/task_manager.py create "Short Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks

  - Environment variable convenience:
    export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks
    python3 ./scripts/task_manager.py create "Short Title" --lane backlog --dir "$HERMES_TASKS_ROOT"

- Always preserve CLI sovereignty: never create, rename, move, or delete task Markdown files by hand. Use the task_manager.py CLI for all operations so sequential IDs, frontmatter, and history remain consistent.

- Re-query the live board after state-changing operations. After create/move/complete calls, run:
    python3 ./scripts/task_manager.py board
  and present the returned view to the user so they see the canonical board state.

- When automating (agents or scripts), prefer the --dir override rather than changing working directory. This keeps behavior predictable across multiple repositories and avoids accidental writes into the wrong project.

- This preference is also persisted in the agent memory store for convenience (so future sessions default to the Hermes Agent tasks path). Skill consumers should rely on SKILL.md guidance first; the memory entry is a convenience, not a substitute for passing --dir explicitly when correctness matters.



The kanban board is a strictly managed directory state. Task IDs must be globally unique and sequentially numbered. The python CLI enforces all of this automatically.

### ❌ WRONG: Manual File Creation (Negative Instruction Constraint)
**AVOID** creating, renaming, moving, or deleting task Markdown files using raw native tools (`write_to_file`, `mv`, `cp`, `rm`) because doing so can bypass the sequential ID generator and risk corrupting the board by creating duplicate numbers or malformed frontmatter.

### ✅ CORRECT: CLI Sovereignty  
**PREFER** `task_manager.py` as the primary interface for kanban operations. When interacting over gateways (WhatsApp, Telegram, Slack), the agent may need to create or update task files directly to accommodate asynchronous message-driven flows; in those cases the agent should:

1. Create a single canonical Markdown file with a provisional ID and clear frontmatter matching the task-manager schema.
2. Immediately run `scripts/task_manager.py sync --adopt /path/to/file` to let the canonical CLI reconcile numbering and register the task properly.
3. After sync, run `scripts/task_manager.py board` and report the live board state back to the user.

When direct file writes are required, the agent must include a comment in the frontmatter noting the original delivery channel (e.g. WhatsApp) and a small audit trail entry so humans can trace provenance.

### ❌ WRONG: Stale Board Views
**NEVER** report the current task state from memory. Boards change between tool calls.

### ✅ CORRECT: Always Re-Query
**ALWAYS** run `task_manager.py board` after any state-change operation to show the user the live, current kanban state.

## Delegated Constraint Verification (L5 Pattern)

When executing `task_manager.py`:
1. If the script exits with code `1` stating a task ID does not exist, do not attempt to manually look for the file in the lane directories. Report the ID as not found and ask the user to confirm.
2. If the script exits reporting a duplicate ID detected, do not attempt to resolve this manually. Consult the `references/fallback-tree.md`.

---

## Project-root resolution & user preference

By default this CLI computes PROJECT_ROOT by walking up from the script location and returning the nearest parent directory that contains a .git folder. That means the effective tasks directory (used when `--dir` is omitted) is PROJECT_ROOT/tasks and will vary depending on which checkout you invoked the script from.

If a user preference exists for which repository should host kanban tasks, prefer honoring that explicit per-user preference. On this host the user prefers the Hermes Agent project root as the canonical tasks root: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`.

Practical guidance — follow these rules when creating or manipulating tasks programmatically or as an agent:

- Honor explicit `--dir` overrides. If a caller provides `--dir`, always use it. Example: `python3 ./scripts/task_manager.py --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks create "Title" --lane backlog`.
- If `--dir` is omitted, prefer a user-configured default (see section "Per-user defaults") before falling back to the computed PROJECT_ROOT/tasks.
- Do NOT attempt to fix or move existing task files across repositories by raw file moves. Use the CLI with `--dir` pointed at the target repo so the ID generator and history remain correct.
- If the computed PROJECT_ROOT differs from the expected repo (common when running the script from a plugin or different checkout), surface a clear warning: `WARNING: computed PROJECT_ROOT is <path>; use --dir to target a different tasks folder`.

Per-user defaults

- Agents and automated scripts SHOULD check for a per-user preference file at `~/.hermes/tasks_default_dir` containing an absolute path to the desired tasks directory. If present and writable, use that as the default `tasks_dir` in lieu of the computed PROJECT_ROOT/tasks. This keeps CLI behavior predictable in multi-repo environments.
- Do NOT hardcode host-specific paths in shared skills; prefer the user preference file or explicit `--dir` flags.

Compatibility and pitfalls

- The CLI's number allocation scans ALL lanes across the configured tasks_dir and picks the next number. Creating tasks in two different repos with different counters will not synchronize IDs: prefer creating in the intended repo only.
- The script's PROJECT_ROOT detection can return surprising results when run from inside nested plugin `.agents/` trees. If you see unexpected paths, use `--dir` or set the per-user default.

## Core Workflows


## Troubleshooting: terminal wrapper backgrounding
If the runtime terminal wrapper returns errors mentioning foreground/backgrounding (for example: "Foreground command uses '&' backgrounding"), the failure is commonly caused by attempting to run many CLI commands in one foreground shell or using shell backgrounding. Best practices:

- Run each `python3 ./scripts/task_manager.py <command>` as a separate terminal call instead of batching multiple commands with `&`, `;`, or long shell scripts. The agent terminal wrapper enforces a foreground/backgrounding guard that can reject grouped commands.
- If a command fails with that message, retry the single command alone; the retry is usually successful.
- Capture and report the created task IDs from each successful create before proceeding to the next step; do not assume creates succeeded in bulk.

This guidance reduces flakiness when agents drive the CLI from the runtime terminal tool.


### 1. Creating a Task (Best Practice)
**Always create the task with a short, descriptive title first to avoid filename length errors.**

```bash
python ./scripts/task_manager.py create "Short Title" --lane todo
```

**After creation, update the generated Markdown file to add full details, objectives, and acceptance criteria.**

This two-step process ensures filenames remain valid and all task details are captured without error.


### Assistant automation preferences (project-specific)
When an assistant or automation creates tasks on behalf of a human, prefer creating fully-populated task files (Objective, Acceptance Criteria, Estimate, and Notes) instead of leaving only stubs. Use the provided populated-task template and pass an explicit --dir when the target project differs from the skill's detected PROJECT_ROOT.

Conventions:
- Default project root override for this user's environment: /Users/richardfremmerlid/Projects/hermes-agent/tasks
- To create a fully-populated task from the CLI (example):

```bash
python3 ./scripts/task_manager.py --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks create "Short Title" --lane backlog --objective "..." --acceptance "..."
```

- Template: templates/populated-task-template.md
- Assistant preference notes: references/assistant_preferences.md

These preferences are **assistant-facing**: humans may still use the two-step create→edit flow, but automated agents should default to producing filled-out tasks so the board is actionable immediately.

### 2. Viewing the Board
```bash
python ./scripts/task_manager.py board
```

### 3. Moving a Task Between Lanes
```bash
python ./scripts/task_manager.py move 3 in-progress --note "Starting work"
```

### 4. Searching Tasks
```bash
python ./scripts/task_manager.py search "login"
```

## 📂 Data Structure
Tasks are Markdown files stored in lane subdirectories (**read-only for the agent, managed exclusively by the CLI**):
- `tasks/backlog/`
- `tasks/todo/`
- `tasks/in-progress/`
- `tasks/done/`
