---
name: create-skill
description: Interactive initialization script that generates a compliant Agent Skill containing the strict YAML frontmatter and Progressive Disclosure 'reference/' block formatting. Use when authoring new workflow routines.
disable-model-invocation: false
---

# Agent Skill Scaffold Generator

You are tasked with generating a new Agent Skill resource using our deterministic backend scaffolding pipeline, while adhering to the official **Agent Skills Open Standard** (`agentskills.io`).

## Core Educational Principles (Enforce These on the User)
Before generating any code, you must review the user's request and ensure the designed skill aligns with the following tenets:

1. **Concise is Key**: The context window is shared. Keep `SKILL.md` under 500 lines. Only add what agents *don't* already know.
2. **Progressive Disclosure**: Split knowledge into physical levels:
   - Metadata (~50 words in YAML)
   - `SKILL.md` body (When triggered)
   - `references/` (Unlimited, loaded on demand)
3. **Structured Bundles**: Use `scripts/` strictly for executable deterministic ops. Use `references/` for docs/guides/tests. Use `assets/` for output templates.

## Execution Steps

### 1. Requirements & Design Phase
Engage the user to clarify the design based on the principles above. Do not jump to scaffolding without understanding:
- **Skill Name**: Must be descriptive.
- **Trigger Description**: The YAML description acts as the LLM trigger. What exactly triggers this?
- **Knowledge Breakdown**: What logic goes in `SKILL.md` vs what should be abstracted to `references/`?
- **Acceptance Criteria**: What defines this skill working correctly?

### 2. Scaffold the Infrastructure
Execute the deterministic `scaffold.py` script to generate the compliant physical directories:
```bash
python3 plugins/scripts/scaffold.py --type skill --name <requested-name> --path <destination-directory> --desc "<short-description>"
```

### 3. Generate Acceptance Criteria
The Open Standard testing best practices explicitly recommend that **every skill MUST have acceptance criteria and test scenarios.**
Using file writing tools, create a new file at `references/acceptance-criteria.md` inside the newly scaffolded skill folder. 
Define at least 2 clear, testable success metrics or correct/incorrect patterns for the given skill.

### 4. Finalize `SKILL.md`
Use file writing tools to populate the generated `SKILL.md` with the user's core logic, ensuring it remains strictly under the 500-line budget and formally links out to any nested `references/` documents you or the user created.
