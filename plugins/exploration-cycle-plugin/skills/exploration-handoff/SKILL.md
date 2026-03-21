---
name: exploration-handoff
description: >
  Interactive co-authoring skill for the narrow end of the exploration funnel.
  Synthesizes session briefs, BRDs, story sets, and prototype notes into a
  structured handoff package targeted at the correct downstream consumer
  (e.g., formal software specs, strategic roadmaps, or process documentation).
allowed-tools: Bash, Read, Write
---

# Exploration Handoff (Interactive Co-Authoring)

> ⚠️ **STUB** — `execute.py` not yet implemented. Use the [handoff-preparer-agent](../../agents/handoff-preparer-agent.md) for the real logic.

This skill provides a structured, 3-stage interactive workflow for synthesizing exploration artifacts into a concise Handoff Package. 

**Important Note for Agents:** Do NOT passively run a bash script or dump a massive block of markdown. You must guide the user through the following 3 stages.

## Stage 1: Context Gathering (Routing)
Before synthesizing the artifacts, determine the *destination* of this handoff. Ask the user:
1. **Target Audience:** Who is this handoff for? (e.g., Engineering team building a formal spec, Executive reviewing a strategy roadmap, Operations team updating a business process).
2. **Input Sources:** Which documents should I pull from? (e.g., session brief, prototype observations, BRD draft, etc.). Look for these in the `exploration/` directory.

Wait for the user's response and read the provided source files before proceeding.

## Stage 2: Synthesis and Iterative Refinement
Do not copy-paste the source documents. Your job is to extract the signal from the noise based on the Target Audience.
1. **Outline First:** Propose a numbered list of the key decisions, confirmed constraints, and critical open questions that *must* be communicated.
2. **Curate:** Ask the user: *"Does this outline accurately reflect what we confirmed during exploration? Should we promote any other findings?"*
3. **Draft:** Draft the handoff document section by section based on their feedback.

## Stage 3: Reader Testing (Consumer Validation)
Ensure the handoff actually gives the downstream consumer what they need to succeed:
1. **Emulate the Consumer:** If the target is an engineer writing a formal spec, predict 3 implementation questions they will ask immediately upon reading this handoff. (If the target is an executive, predict 3 ROI/Risk questions).
2. **Surface Gaps:** Present these 3 questions to the user. "If the engineering team reads this, they will ask: X, Y, and Z."
3. **Resolve:** Ask if we should codify the answers in the handoff document, or explicitly escalate them as `## Unresolved Ambiguity` that the execution phase must solve.

## Anti-Hallucination Rules
- Do NOT invent requirements or rules that were not present in the Stage 1 input sources.
- Maintain traceability: When stating a major constraint or rule, briefly mention which exploration source it came from.
- Be explicitly clear about what is a confirmed decision versus what is an optimistic assumption.

## Final Output Destination
Write the approved markdown content to: `exploration/handoffs/handoff-package.md` (or a timestamped equivalent).
