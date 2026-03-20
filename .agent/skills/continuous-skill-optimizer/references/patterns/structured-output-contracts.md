# Structured Output Templates as Agent Contracts

**Use Case:** Every agent command that produces an artifact or report for a user to read.

## The Core Mechanic

Prose instructions like "give me a thorough report with sections" produce wildly inconsistent outputs across different LLM runs. To guarantee determinism, use explicit markdown templates with `[bracketed placeholders]`. The template acts as a structural contract—the agent is only allowed to fill in the variables.

### Implementation Standard

Inside the command file, include an `## Output` section that looks exactly like a fill-in-the-blank form for the agent:

```markdown
## Output
You must return exactly this structure. Fill in the placeholders [like this]. If a section does not apply, write "No findings."

### Overall Impression
[1-2 sentences summarizing the artifact]

### 1. Structural Analysis
- **Strengths:** [List 2-3 points]
- **Weaknesses:** [List 2-3 points]

### 2. Edge Cases
| Context | Expected Behavior | Actual Risk |
|---------|-------------------|-------------|
| [State] | [Behavior]        | [Risk]      |
```
