---
concept: structured-output-templates-as-agent-contracts
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/structured-output-contracts.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.015825+00:00
cluster: plugin-code
content_hash: d71e1a29359b340c
---

# Structured Output Templates as Agent Contracts

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[structured-output-contracts]]
- [[structured-output-contracts]]
- [[structured-output-contracts]]
- [[structured-output-contracts]]
- [[structured-output-contracts]]
- [[structured-output-contracts]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/structured-output-contracts.md`
- **Indexed:** 2026-04-17T06:42:10.015825+00:00
