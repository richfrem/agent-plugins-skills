---
name: create-stateful-skill
plugin: agent-scaffolders
description: >
  Scaffolds an advanced stateful agent skill with filesystem-native state schemas, lifecycle state
  machines, and skill chaining. NOT for simple stateless skills (use `create-skill`), NOT for
  isolated conversational wizards / persona swarms (use `create-sub-agent`), and NOT for GitHub
  Actions workflows (use `create-agentic-workflow`).
argument-hint: "[skill-name]"
allowed-tools: Bash, Read, Write
---

Follow the `create-stateful-skill` workflow to scaffold an advanced agent skill with
L4 state management, lifecycle artifacts, and deterministic skill chaining.

> [!IMPORTANT]
> **Stateful Skill vs. Guided Sub-Agent Boundary (2026+)**
> - **Stateful Skill (`create-stateful-skill`)**: Runs directly in the main conversation. Persists state
>   across separate turns via filesystem schemas (`.agent/learning/`, `.agent/state/`, or artifact frontmatter).
>   Best for: lifecycle state transitions (Draft → Review → Final), cyclical workflows, persistent configs, and chained skill steps.
> - **Guided Workflow Sub-Agent (`create-sub-agent`)**: Runs in an isolated forked context (`context: fork`).
>   Best for: long multi-turn conversational interviews or setup wizards where intermediate chatter must not pollute the main session.
> - **Stateless Procedural Skill (`create-skill`)**: Use when no cross-turn state, counters, or schemas are needed.

## Inputs

- `$ARGUMENTS` — optional skill name or use-case description. Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` provides a skill name or context, use it to seed discovery.
2. **Pre-Scaffold Qualification**: Verify that the skill requires cross-turn state (if not, redirect to `create-skill`).
3. Follow the phased workflow:
   - Identify required L4 patterns from `pattern-decision-matrix.md` (artifact lifecycle, cyclical state propagation, persistent configuration, escalation taxonomy).
   - Design the state schema (JSON/YAML in `.agent/state/` or artifact frontmatter metadata).
   - Design skill chaining via standard Offer-Next-Steps blocks (linking to subsequent `/skill-name` capabilities, not legacy flat commands).
   - Scaffold the skill directory: `SKILL.md` (< 100-500 lines), `evals/evals.json`, `references/` (offloaded schemas & rules).
4. Run `audit_skill.py` to verify compliance.
5. Report created skill path, state schema, and next-step execution sequence.

## Output

Skill directory with `SKILL.md` implementing selected L4 patterns, explicit state schemas,
lifecycle artifact templates, and skill-chaining transitions.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with discovery — identify which L4 patterns apply.
- If the use case is simple (no persistent state, no chaining): recommend `create-skill` instead.
- If the workflow requires multi-turn human interview loops: recommend `create-sub-agent` instead.
- If state mutations are high-risk: configure escalation taxonomy steps and human confirmation gates.
