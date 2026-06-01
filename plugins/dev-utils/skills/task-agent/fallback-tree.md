# Procedural Fallback Tree: Task Manager

If the primary task management CLI (`./../scripts/task_manager.py`) fails, execute the following triage steps exactly in order:

## 1. Task ID Not Found
If `./../scripts/task_manager.py move` or `./../scripts/task_manager.py get` exits with code `1` stating a task ID does not exist:
- **Action**: Do not scan the `tasks/` directory manually to find the file. Run `./../scripts/task_manager.py board` or `list` to retrieve the full current list of task IDs, present the live list to the user, and ask them to confirm the correct ID.

## 2. Duplicate Task ID Detected
If the CLI throws an error about a duplicate task ID when creating or moving:
- **Action**: This means the number sequence in the board has been corrupted by a manual file edit on a previous occasion. Do not try to auto-resolve this by deleting or renaming the duplicate directly. Report the corruption to the user and ask for permission to remove the conflicting file manually.

## 3. Missing Lane Directory
If `./../scripts/task_manager.py` reports a lane directory (e.g. `tasks/in-progress/`) does not exist:
- **Action**: Do not manually create the lane directory. Report the issue to the user explaining the expected directory structure is missing and the board needs to be re-initialized.
