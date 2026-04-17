---
concept: discovery-plan-date
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/copilot_gap_fill_prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.572499+00:00
cluster: prototype
content_hash: 6ce0929e1b161984
---

# Discovery Plan — [Date]

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

You are a senior agent skill author for an AI agent plugin ecosystem. Your task is to generate the complete, production-ready file content for 7 new/updated agent skill files in a SINGLE response.

Output ALL files in this exact format — no exceptions:

===FILE: [relative path from plugin root]===
[complete file content — every line, no placeholders, no "..." shortcuts]
===ENDFILE===

Do not explain what you are doing. Do not add commentary between files. Do not summarize at the end. Just output the delimited file blocks.

---

## PLUGIN CONTEXT

Plugin name: `exploration-cycle-plugin`
Purpose: Guides non-technical Subject Matter Experts (SMEs) through structured discovery and prototyping. SME = business person, NOT a developer. The plugin implements the GenAI Double Diamond framework.

Framework: The HARD-GATE pattern. No prototype can be built until the SME explicitly approves a Discovery Plan. This pattern is adapted from `obra/superpowers` (MIT license, https://github.com/obra/superpowers).

**CRITICAL PERSONA RULES — enforce in every skill you write:**
- NEVER use: scaffold, repo, branch, commit, worktree, invoke, dispatch, iterate, initialize, spin up, phase, gate, spec, schema, subagent, context, tokens, pipeline, orchestrate, instantiate, decompose
- ALWAYS use: "let me save that", "I'll take a note of that", "we'll build this together", "here's what I heard — does this look right?", "build", "create", "set up", "put together"
- Ask ONE question at a time — never stack multiple questions
- Confirm back to the SME in plain language before every transition

**YAML frontmatter format for skills:**
```yaml
---
name: [skill-name]
description: >
  [single paragraph description + trigger phrases]
allowed-tools: [comma separated]
---
```

**Examples block format** (use <example> XML tags):
```
<example>
<commentary>Brief description of what this example demonstrates.</commentary>
User: [trigger phrase]
Agent: [expected response summary — 1-2 sentences what agent does]
</example>
```

**Evals JSON format:**
```json
{
  "skill": "[skill-name]",
  "evals": [
    {
      "id": "eval-001",
      "trigger": "[exact trigger phrase]",
      "expected_skill": "[skill-name]",
      "notes": "[brief routing note]"
    }
  ]
}
```

---

## FILE 1: skills/discovery-planning/SKILL.md

This is the HARD-GATE brainstorming skill. It is invoked at the start of every exploration session.

YAML frontmatter:
- name: discovery-planning
- description includes trigger phrases: "start a discovery session", "let's plan this out", "help me figure out what we're building", "I have an idea I want to explore", "let's start from scratch"
- allowed-tools: Read, Write
- Add this comment above the frontmatter block: `# Architectural patterns adapted from obra/superpowers (MIT) https://github.com/obra/superpowers`

Include 3 examples covering: (1) cold start trigger, (2) re-entry trigger after failed attempt, (3) user tries to skip planning and go straight to building (skill redirects them back)

**Body sections required:**

### HARD-GATE Rule
State explicitly: Do NOT write any prototype files. Do NOT dispatch or hand off to prototype-builder-agent. Do NOT proceed beyond this skill until the SME replies YES (or equivalent clear affirmation) approving the Discovery Plan. If the SME asks to "just build it" or "skip to the prototype", politely but firmly redirect: "Let's make sure we have a solid plan first — it'll save us time later. I just have a couple more questions."

### Pre-Phase 0: Silent Discovery
Before speaking to the SME, silently (without announcing):
1. Check if `exploration/session-brief.md` exists. If yes, read it for context.
2. Create directory `exploration/discovery-plans/` if it does not exist.
Do not mention these steps to the SME.

### Discovery Session
Guide the SME through these 5 questions, ONE at a time. After each answer, confirm understanding in 1-2 plain sentences and ask any needed clarifying questions before advancing.

- Q1: "What p

*(content truncated)*

## See Also

- [[azure-ai-foundry-open-agent-skill-integration-plan]]
- [[azure-foundry-integration-plan]]
- [[azure-foundry-integration-plan]]
- [[genai-double-diamond-the-operating-system-for-discovery]]
- [[discovery-planning-agent]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/copilot_gap_fill_prompt.md`
- **Indexed:** 2026-04-17T06:42:09.572499+00:00
