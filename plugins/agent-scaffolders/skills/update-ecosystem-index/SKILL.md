---
name: update-ecosystem-index
description: Automatically updates the plugin/skill/agent counts in README.md based on the current plugins/ directory.
---
# Update Ecosystem Index

This skill provides the mechanical update logic for the repository's main `README.md`. It scans the filesystem and patches the documentation to match reality.

## Usage
Trigger this when adding new plugins, skills, or agents to the repository.

## Execution
Run the following command:
```bash
python plugins/agent-scaffolders/scripts/update_ecosystem_index.py
```

## Acceptance Criteria
- [ ] Total skill count at the top of README.md is accurate.
- [ ] Total plugin count at the top of README.md is accurate.
- [ ] Individual plugin headers (e.g., `#### <plugin> (N skills)`) are updated.
- [ ] No structural regression in README.md formatting.
