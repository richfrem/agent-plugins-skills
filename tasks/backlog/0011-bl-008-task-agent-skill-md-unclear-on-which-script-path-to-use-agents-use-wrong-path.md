# Task 0011: BL-008: task-agent SKILL.md unclear on which script path to use - agents use wrong path

## Objective
task-agent SKILL.md does not clearly specify whether to call scripts from plugins/task-manager/skills/task-agent/scripts/ or .agent/skills/task-agent/scripts/. This session used the .agent/ installed path - unclear if that is correct or if plugin source path should be used. SKILL.md needs explicit canonical path with rationale.

## Acceptance Criteria
task-agent SKILL.md specifies exactly which path to invoke task_manager.py and next_number.py from, with explanation of why. No ambiguity between plugin source and installed paths.

## Notes
