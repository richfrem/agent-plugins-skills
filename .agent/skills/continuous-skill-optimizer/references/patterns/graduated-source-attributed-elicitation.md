# Graduated Source-Attributed Knowledge Elicitation

**Status:** Draft
**Pattern Type:** Interaction Pattern
**Applicable Domain:** Scaffolding, Discovery Interviews, Requirements Gathering

## Executive Summary
Organizational knowledge needed to parameterize an operation is gathered through a tiered, source-ordered pipeline. The provenance of each answer is tracked throughout execution, and the final workflow summary is structured by source provenance rather than by what was changed.

## The Abstract Problem
When setting up a plugin or scaffolding a project, an agent needs answers to questions (e.g., "What is your project tracker?"). Default agents ask the user everything, causing extreme fatigue. Better agents try to use knowledge MCPs first. But standard patterns lose track of *where* the answer came from, leading to opaque summaries ("I configured Jira") where the user doesn't know if they said that or if the agent guessed it.

## The Target
Any interactive, multi-step knowledge-gathering or configuration workflow.

## The Core Mechanic
Knowledge is gathered in strict priority order:
1. User phase-zero free-form prompt
2. Automated Knowledge MCP searches
3. Explicit User Questions

All gathered variables are tagged with their source. The final summary presents findings grouped by provenance: "From Slack", "From Documents", "From your answers".

## Distinction from Similar Patterns
- **Priority-Ordered Source Scanning**: Scans data systems to find facts efficiently. GSAKE extends this to include the user themself in the priority queue and strictly forces provenance-surfacing in the output.
- **Guided Discovery Interview**: A conversational structure for questions. GSAKE dictates *how* to avoid asking questions in the first place, and how to attribute the answers.

## Implementation Standard

```markdown
1. Phase 0: Always accept a free-form input first.
2. Phase 1: Search connected knowledge systems (e.g., Slack, Docs) for any missing parameters.
3. Phase 2: Only use `AskUserQuestion` for what remains unknown.
4. If the user skips a question, leave the parameter undefined.
5. In the final output, group the summary by source:
   ### From searching Slack
   - You use Jira for tickets
   ### From your answers
   - You want daily standups at 9am
```

## Anti-Patterns
1. **The Interrogation**: Asking the user a question before attempting to find the answer in an available MCP knowledge base.
2. **The Origin Scrub**: Summarizing the final configuration without explicitly stating where the variables were sourced from.
