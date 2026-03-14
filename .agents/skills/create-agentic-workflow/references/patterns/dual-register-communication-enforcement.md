# Dual-Register Communication Enforcement

**Status:** Draft
**Pattern Type:** Output Pattern
**Applicable Domain:** Copilots, Customization, Debugging, Deployment

## Executive Summary
The skill maintains two strictly separated communication registers throughout execution: a technical register used for internal commands and tool calls, and a semantic register used exclusively for user-visible outputs (todo lists, summaries, questions), ensuring technical mechanics are completely abstracted from the user.

## The Abstract Problem
Agents naturally parrot the terminology of the codebase they are manipulating. If an agent is manipulating `yaml` placeholders, `json` schemas, or finding `~~` sigils, it will generate todo lists like "Replace ~~chat with slack in configs/plugin.yaml". This forces the user to understand the plugin's internal mechanics rather than its capability.

## The Target
Any workflow where the agent performs highly technical manipulation of templates, configs, or metadata on behalf of a non-developer or a user focused on the pure outcome.

## The Core Mechanic
An explicit architectural constraint is placed on all user-facing generation blocks (AskUserQuestion, Headers, Todo Lists). The agent is explicitly forbidden from exposing the technical register to the user, forcing a translation layer between its internal `tool execution` and its external `communication`.

## Distinction from Similar Patterns
- **Impact-Translated Status**: Translates metrics (numbers) into business impact. DRCE translates technical implementation mechanics (files/tokens) into semantic workflow capabilities.
- **Audience-Segmented Filtering**: Decides what to reveal vs hide based on who is listening. DRCE is a universal translation constraint for the primary user.

## Implementation Standard

```markdown
### Communication Register Rule
You must maintain a strict technical/semantic boundary.
- **Internal Register**: Use precise technical terms (file paths, `~~` placeholders, object keys) in your reasoning and tool calls.
- **User-Facing Register**: NEVER expose the technical register to the user. Translate everything into semantic workflow terminology.

- **BAD TODO**: "Replace ~~chat placeholder in `setup.py`"
- **GOOD TODO**: "Configure the team chat integration"
```

## Anti-Patterns
1. **The Leaky Abstraction**: Emitting raw tool payloads or file paths in the conversation summary.
2. **The Developer Parroting**: Using sigils like `~~` or `{{` in the text of a question posed to the user.
