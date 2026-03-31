# Task 0010: BL-007: plugin-installer not copying assets/ directory during plugin install

## Objective
plugins/task-manager/assets/templates/task-template.md exists in source but is missing from .agent/skills/task-agent/ after plugin-installer install. plugin-installer SKILL.md maps skills/ commands/ rules/ hooks/ but has no mapping for assets/. Templates are inaccessible to installed skills.

## Acceptance Criteria
plugin-installer installs assets/ directory contents to appropriate target path. task-template.md appears in .agent/skills/task-agent/assets/templates/ after install.

## Notes
