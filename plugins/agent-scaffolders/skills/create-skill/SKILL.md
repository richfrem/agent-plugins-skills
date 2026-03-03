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
Use a guided discovery interview to understand the skill design. Ask questions progressively (broad → specific → confirmation).

Before proceeding, read the `references/hitl-interaction-design.md` guide to understand the full spectrum of input interaction patterns and output template options available.

**Core Questions:**
- **Skill Name**: Must be descriptive, kebab-case. Use gerund form when possible (e.g., `analyzing-legacy-code`).
- **Trigger Description**: The YAML description acts as the LLM trigger. What exactly triggers this? Write in third person.
- **Knowledge Breakdown**: What logic goes in `SKILL.md` vs what should be abstracted to `references/`?
- **Acceptance Criteria**: What defines this skill working correctly?

**Interaction Design Questions (present as numbered options):**
- **Execution Mode**: Does this skill need dual modes?
  ```
  1. Single mode — always starts fresh
  2. Dual mode — Bootstrap (create new) + Iteration (improve existing)
  ```
- **User Interaction Style**:
  ```
  1. Autonomous — runs without user input after trigger
  2. Guided — interviews user before executing (discovery phase)
  3. Hybrid — gathers minimal context, then executes with confirmation gates
  ```
- **Output Format**: What should the skill produce, and who/what consumes it downstream?
  ```
  1. Inline markdown (human reads in chat)
  2. Structured report with sections (human reads as document)
  3. HTML artifact (human views as dashboard/visual)
  4. JSON export (machine/pipeline consumes)
  5. CSV export (spreadsheet/analytics consumes)
  6. Multiple formats (negotiate with user at runtime)
  ```

### 2. Scaffold the Infrastructure
Execute the deterministic `scaffold.py` script to generate the compliant physical directories:
```bash
python3 plugins/scripts/scaffold.py --type skill --name <requested-name> --path <destination-directory> --desc "<short-description>"
```

### 3. Generate Acceptance Criteria
The Open Standard testing best practices explicitly recommend that **every skill MUST have acceptance criteria and test scenarios.**
Using file writing tools, create a new file at `references/acceptance-criteria.md` inside the newly scaffolded skill folder.
Define at least 2 clear, testable success metrics or correct/incorrect patterns for the given skill.

### 4. Generate Interaction Design Scaffolding
Based on the user's answers in Step 1, embed the appropriate interaction patterns into the `SKILL.md`:

- **If Guided**: Add a `## Discovery Phase` section with progressive questions
- **If Dual-Mode**: Add `## Bootstrap Mode` and `## Iteration Mode` sections
- **If Output Negotiation**: Add an output format menu before the execution phase
- **Always**: Add a `## Next Actions` section at the end offering follow-up options
- **If Expensive Operations**: Add confirmation gates before destructive/costly steps

### 5. Finalize `SKILL.md`
Use file writing tools to populate the generated `SKILL.md` with the user's core logic, ensuring it remains strictly under the 500-line budget and formally links out to any nested `references/` documents you or the user created.
