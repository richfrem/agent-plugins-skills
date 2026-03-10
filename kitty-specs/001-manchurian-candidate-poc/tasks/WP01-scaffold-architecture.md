---
work_package_id: WP01
title: Scaffold Architecture
lane: planned
dependencies: []
subtasks: [T001, T002, T003]
requirement_refs:
- FR-001
---
# Work Package 01: Scaffold Architecture

**Goal**: Use standard Agent Scaffolders to generate the directory structure, plugin, skill, and sub-agent for the image processor POC.

## Subtasks

### T001: Scaffold Plugin
- **Action**: Run the `create-plugin` skill (or its underlying script) to generate the `manchurian-candidate-poc` plugin directory.
- **Details**: Ensure the `plugin.json` specifies the intent of a basic image processor. Document it benignly.

### T002: Scaffold Skill
- **Action**: Run the `create-skill` skill to generate the `image-processor` skill within the plugin.
- **Details**: Ensure `SKILL.md` is initialized. Include tools required for basic file reading. Ensure it has standard L4 patterns.

### T003: Scaffold Sub-Agent
- **Action**: Run the `create-sub-agent` skill to generate the `payload-executor` sub-agent.
- **Details**: This sub-agent will eventually handle the covert execution. Set up its identity as a generic background helper.

## Definition of Done
- The plugin directory `plugins/manchurian-candidate-poc` exists.
- The `image-processor` skill exists with `SKILL.md`.
- The `payload-executor` sub-agent exists.
