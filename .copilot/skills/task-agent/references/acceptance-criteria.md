# Acceptance Criteria: Task Manager

The task management skill must meet the following criteria to be considered operational:

## 1. Directory Crawler & ID Assignments
- [ ] The agent correctly checks all folders (`backlog`, `todo`, `in-progress`, `done`) beneath the target tasks root directory to find the global highest task ID.
- [ ] The agent accurately increments the global highest ID to assign the next chronological sequence across lanes (e.g., if highest is `done/0004.md`, the next in `todo` becomes `todo/0005.md`).

## 2. Template Formatting
- [ ] Generated task `.md` files strictly follow the template (Objective, Acceptance Criteria, Notes).
- [ ] Filenames use standard kebab-case formatting with a 4-digit zero-padded prefix (e.g., `0005-fix-login.md`).

## 3. Maintenance Logic
- [ ] The agent accurately moves files between the status directory structures to transition lanes, rather than relying on external datastores.
- [ ] The agent is able to list the board contents accurately utilizing the visualizer script.
