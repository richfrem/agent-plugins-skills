Session-specific note: user preference and environment

- Preferred Hermes tasks root (user-specific):
  /Users/richardfremmerlid/Projects/hermes-agent/tasks

- Rationale: user asked task-agent operations to default to the Hermes Agent project. This file exists to be referenced by SKILL.md and by future agents.

- How to use:
  - CLI: python3 ./scripts/task_manager.py create "Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks
  - Env var convenience: export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks
  - Agents: pass --dir argument when invoking the script rather than changing cwd.
