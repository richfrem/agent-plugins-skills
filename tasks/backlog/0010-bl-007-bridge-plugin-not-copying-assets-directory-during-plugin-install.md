# Task 0010: BL-007: bridge-plugin not copying assets/ directory during plugin install

## Objective
plugins/task-manager/assets/templates/task-template.md exists in source but is missing from .agent/skills/task-agent/ after bridge-plugin install. bridge-plugin SKILL.md maps skills/ commands/ rules/ hooks/ but has no mapping for assets/. Templates are inaccessible to installed skills.

## Acceptance Criteria
bridge-plugin installs assets/ directory contents to appropriate target path. task-template.md appears in .agent/skills/task-agent/assets/templates/ after install.

## Notes
