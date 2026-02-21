---
name: create-skill
description: Interactive initialization script that generates a compliant Agent Skill containing the strict YAML frontmatter and Progressive Disclosure 'reference/' block formatting. Use when authoring new workflow routines.
disable-model-invocation: false
---

# Agent Skill Scaffold Generator

You are tasked with generating a new Agent Skill resource using our deterministic backend scaffolding pipeline.

## Execution Steps:

1. **Gather Requirements:**
   Ask the user for:
   - The name of the skill.
   - The short description of its purpose.
   - Where it should be placed (e.g. inside an existing plugin, inside a project `.claude/skills/`, or a global `.agent/skills/` folder).

2. **Scaffold the Skill:**
   You must execute the hidden deterministic `scaffold.py` script included in this plugin to guarantee perfect Open Standard compliance (correct YAML frontmatter, 500-line warning limits, and Progressive Disclosure folder trees).
   
   Run the following bash command:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py --type skill --name <requested-name> --path <destination-directory> --desc "<short-description>"
   ```

3. **Confirmation:**
   Print a success message showing the paths generated, and advise the user to edit the structured `SKILL.md` and `reference/` block to establish their prompt logic.
