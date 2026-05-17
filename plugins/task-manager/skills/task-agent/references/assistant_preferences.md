Assistant preferences for task creation and placement

- Default project root for this user's task operations: /Users/richardfremmerlid/Projects/hermes-agent/tasks
- Always populate new tasks with full content (Objective, Acceptance Criteria, Estimates, Notes) unless the user explicitly requests stubs.
- When the skill's automatic PROJECT_ROOT detection differs from the user's preferred root, pass --dir to the CLI to target the preferred root.
- Use templates/populated-task-template.md as the basis for content structure.
- After creating tasks, run `python3 ./scripts/task_manager.py --dir <root> board` to refresh the live view and report back to the user.
