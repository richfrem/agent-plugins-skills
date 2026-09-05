---
name: create-sub-agent
plugin: agent-scaffolders
description: >
  Scaffolds a new autonomous sub-agent with its own prompt, system instructions, and tool permissions.
  Enforces modern architectural guidance: sub-agents are reserved for isolated execution contexts,
  strict tool sandboxing, or adversarial personas. NOT for simple procedural skills (use `create-skill`)
  and NEVER for pointer-wrapper stubs that merely delegate to a skill.
argument-hint: "[agent-name or use-case description]"
allowed-tools: Bash, Read, Write
---

Follow the `create-sub-agent` skill workflow to design and generate a Claude Code / Copilot agent file.

> [!IMPORTANT]
> **Modern Agent Guidance (2026+): When to Create a Sub-Agent vs. a Skill**
> 
> In modern agentic systems, sub-agents serve two distinct high-value archetypes that skills alone cannot fulfill cleanly:
> 
> 1. **Guided Workflow Wizards (Interactive Discovery & Onboarding)**:
>    - Multi-turn conversational interviews (e.g. `wiki-init-agent`, `vector-db-init-agent`, `intake-agent`).
>    - Requires asking one question at a time, probing the environment dynamically, and generating a verified configuration.
>    - Uses **context isolation (`context: fork`)** to shield the parent workspace conversation from hundreds of lines of interactive wizard chatter.
> 
> 2. **Persona Specialists & Adversarial Swarms**:
>    - Independent critical evaluation (e.g. `security-auditor`, `tdd-contract-reviewer`, `compliance-reviewer`).
>    - Adopts an unyielding, specialized mindset distinct from the cooperative pairing assistant.
>    - Uses **tool sandboxing** (e.g. `permissions.deny: ["Bash", "Write"]`) to ensure the agent cannot alter code.
> 
> **When to use a Skill (`create-skill`) instead:**
> - Stateless, direct procedural execution, deterministic task scripts, or routine tools that belong in the main session flow.
> 
> **The Anti-Pattern to NEVER Create:**
> - **Pointer-Wrapper Stubs**: Never create a 10-line agent whose body is merely *"Please run the `<name>` skill immediately."* Runtimes already invoke skills directly; stubs create duplicate discovery noise.

## Inputs

- `$ARGUMENTS` — optional agent name or brief use-case description passed as initial context
  to the design interview. Omit to start with open discovery.

## Steps

1. If `$ARGUMENTS` is provided, use it as the starting context for agent name / purpose.
2. **Pre-Design Gate**: Verify that the use-case genuinely requires an autonomous sub-agent rather than a skill. If it is a procedural routine, redirect to `create-skill`.
3. Follow the phased workflow: extract core intent via design interview
   (purpose, input/output contract, escalation posture, tools, permissions.deny, model,
   maxTokens, color, lifecycle hooks, placement), present design summary, confirm,
   then generate the agent `.md` file.
4. Validate the generated agent with `validate_agent.py`.
5. **Publication Check**: Ask if the agent should be visible to GitHub Copilot or Claude Code for this repository. If yes, materialize it into `.github/agents/` or `.claude/agents/` and ensure the path is tracked in `.gitignore`.
6. Report the created agent path, triggering conditions, and next steps.

## Output

Agent `.md` file with complete YAML frontmatter (name, description with `<example>` blocks,
model, maxTokens, color, permissions.allowedTools, permissions.deny) and a second-person
system prompt targeting 500-3,000 characters.

## Placement Rules

**Plugin agents**: flat `.md` file — `plugins/<plugin-name>/agents/<agent-name>.md`
- **No subdirectory.** Skills use `skills/<name>/SKILL.md` subdirectory format, but agents do NOT.
- Confirmed against Anthropic official plugins (`feature-dev`, `code-simplifier`, `hookify`).

**Local/project agents**: `.claude/agents/<agent-name>.md` (also flat, no subdirectory).

## Discovery & Publication

To make an agent visible to GitHub Copilot or Claude Code for this repository, follow the **Discovery-First Publication** pattern:
1. Materialize the agent into `.github/agents/` (Copilot) or `.claude/agents/` (Claude).
2. Ensure `.gitignore` allows the specific agent file or subdirectory.
3. Commit the materialized file to the repository.

See [Agent Discovery and Publication Pattern](../../references/agent-discovery-and-publication.md) for details.

## Edge Cases

- If `$ARGUMENTS` is empty: conduct the full Phase 1 design interview — do not pre-fill
- If an agent with that name already exists: confirm before overwriting
- If requirements suggest multiple responsibilities: propose splitting into specialized agents
- If high-risk operations are required: configure escalation posture and add Stop hook
