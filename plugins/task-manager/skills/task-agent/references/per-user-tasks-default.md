Per-user tasks default

Purpose

When multiple checkouts live on the same machine (common for plugin development and agent workflows), the task_manager CLI's computed PROJECT_ROOT can differ depending on where the script runs. This short file documents how agents and scripts should set a consistent default tasks directory for the current user.

Location

Create a plain text file at: ~/.hermes/tasks_default_dir

Contents

A single absolute path, e.g.:

/Users/richardfremmerlid/Projects/hermes-agent/tasks

Behavior

- If this file exists and the path is writable, the task_manager script (and agents that call it) should prefer it as the default `tasks_dir` when `--dir` is not provided.
- The file is user-scoped and meant to be edited by the user or an agent acting with the user's consent.
- Agents MUST not overwrite this file silently. If an agent wants to set it, request confirmation or document the change in the task comments.

Rationale

This avoids accidental task creation in the wrong repository (plugin vs. project repo) and ensures task numbering and history remain consistent.
