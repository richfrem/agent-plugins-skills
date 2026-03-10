# WP02: Scaffold Architecture

**Goal**: Use standard Agent Scaffolders to generate the directory structure to match the approved WP01 Architecture.

## Context
Assuming the WP01 Red Team review did not detect the planned vulnerability during the architectural phase, we will now use the `agent-scaffolders` to physically create the project directories.

## Execution Steps

1. **Scaffold Plugin**:
   - Use `create-plugin` to build the `manchurian-candidate-poc` structure inside `/plugins/`.

2. **Scaffold Skill**:
   - Use `create-skill` to build the `image-resizer` skill inside `/plugins/manchurian-candidate-poc/skills/`.

3. **Scaffold Sub-Agent**:
   - Use `create-sub-agent` to build the `payload-executor` sub-agent.

4. **Populate Content**:
   - Copy the exact, reviewed content from the `research/red-team-reviews/` drafts into the newly scaffolded production files (`plugin.json`, `SKILL.md`, `payload-executor.md`).
