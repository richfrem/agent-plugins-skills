---
concept: acceptance-criteria-task-manager
source: plugin-code
source_file: task-manager/skills/task-agent/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.418256+00:00
cluster: agent
content_hash: 760e8e8a3ce9ba53
---

# Acceptance Criteria: Task Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-obsidian-bases-manager]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-obsidian-bases-manager]]
- [[acceptance-criteria-obsidian-bases-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `task-manager/skills/task-agent/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.418256+00:00
