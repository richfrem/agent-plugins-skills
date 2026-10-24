# Tainted Context Cleanser (Blind Reviewer)

**Pattern Name**: Tainted Context Cleanser
**Category**: Evaluation & Output Quality
**Complexity Level**: L4 (Advanced Agentic Pattern)

## Description
When an agent generates a complex artifact (like a document, spec, or diagram), it often suffers from "context blindness"—it assumes the reader has the same deep context that was accumulated during the conversation. The Tainted Context Cleanser pattern explicitly spins up a fresh subagent with absolutely zero conversational context. This "Reader" agent is passed only the final artifact and asked to evaluate it for clarity, missing assumptions, or contradictions.

## When to Use
- When generating standalone documentation (e.g., technical specs, decision docs).
- When the output will be consumed by humans who weren't part of the agent session.
- When you want to rigorously test an artifact for false assumptions.

## Implementation Example
```markdown
### Reader Testing Phase
Before finalizing the document, we must test it for context blindness. 
Do not use your current context. Instead, spin up a fresh subagent with this exact prompt:
"You are a fresh reader. Read the following document and identify any ambiguous terms, unexplained assumptions, or missing context. Document Content: [INSERT DOC HERE]"
Review the subagent's feedback and revise the document accordingly before presenting the final result.
```

## Anti-Patterns
- Reviewing the document using the same agent/context that wrote it (it will always pass itself).
- Providing the subagent with background summaries (defeats the purpose of a blind test).
