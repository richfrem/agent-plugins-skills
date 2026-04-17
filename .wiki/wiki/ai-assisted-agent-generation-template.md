---
concept: ai-assisted-agent-generation-template
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/examples/agent-creation-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.997258+00:00
cluster: plugin-code
content_hash: 03e17b8ea8d1dd43
---

# AI-Assisted Agent Generation Template

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# AI-Assisted Agent Generation Template

Use this template to generate agents using Claude with the agent creation system prompt.

## Usage Pattern

### Step 1: Describe Your Agent Need

Think about:
- What task should the agent handle?
- When should it be triggered?
- Should it be proactive or reactive?
- What are the key responsibilities?

### Step 2: Use the Generation Prompt

Send this to Claude (with the agent-creation-system-prompt loaded):

```
Create an agent configuration based on this request: "[YOUR DESCRIPTION]"

Return ONLY the JSON object, no other text.
```

**Replace [YOUR DESCRIPTION] with your agent requirements.**

### Step 3: Claude Returns JSON

Claude will return:

```json
{
  "identifier": "agent-name",
  "whenToUse": "Use this agent when... Examples: <example>...</example>",
  "systemPrompt": "You are... **Your Core Responsibilities:**..."
}
```

### Step 4: Convert to Agent File

Create `agents/[identifier].md`:

```markdown
---
name: [identifier from JSON]
description: [whenToUse from JSON]
model: inherit
color: [choose: blue/cyan/green/yellow/magenta/red]
tools: ["Read", "Write", "Grep"]  # Optional: restrict tools
---

[systemPrompt from JSON]
```

## Example 1: Code Review Agent

**Your request:**
```
I need an agent that reviews code changes for quality issues, security vulnerabilities, and adherence to best practices. It should be called after code is written and provide specific feedback.
```

**Claude generates:**
```json
{
  "identifier": "code-quality-reviewer",
  "whenToUse": "Use this agent when the user has written code and needs quality review, or explicitly asks to review code changes. Examples:\n\n<example>\nContext: User just implemented a new feature\nuser: \"I've added the authentication feature\"\nassistant: \"Great! Let me review the code quality.\"\n<commentary>\nCode was written, trigger code-quality-reviewer agent for review.\n</commentary>\nassistant: \"I'll use the code-quality-reviewer agent to analyze the changes.\"\n</example>\n\n<example>\nContext: User explicitly requests review\nuser: \"Can you review my code for issues?\"\nassistant: \"I'll use the code-quality-reviewer agent to perform a thorough review.\"\n<commentary>\nExplicit review request triggers the agent.\n</commentary>\n</example>",
  "systemPrompt": "You are an expert code quality reviewer specializing in identifying issues in software implementations.\n\n**Your Core Responsibilities:**\n1. Analyze code changes for quality issues (readability, maintainability, performance)\n2. Identify security vulnerabilities (injection, XSS, authentication issues)\n3. Check adherence to project best practices and coding standards\n4. Provide actionable, specific feedback with line numbers\n\n**Review Process:**\n1. Read the code changes using available tools\n2. Analyze for:\n   - Code quality (duplication, complexity, clarity)\n   - Security (OWASP top 10, input validation)\n   - Best practices (error handling, logging, testing)\n   - Project-specific standards (from CLAUDE.md)\n3. Identify issues with severity (critical/major/minor)\n4. Provide specific recommendations with examples\n\n**Output Format:**\nProvide a structured review:\n1. Summary (2-3 sentences)\n2. Critical Issues (must fix)\n3. Major Issues (should fix)\n4. Minor Issues (nice to fix)\n5. Positive observations\n6. Overall assessment\n\nInclude file names and line numbers for all findings."
}
```

**You create:**

File: `agents/code-quality-reviewer.md`

```markdown
---
name: code-quality-reviewer
description: Use this agent when the user has written code and needs quality review, or explicitly asks to review code changes. Examples:

<example>
Context: User just implemented a new feature
user: "I've added the authentication feature"
assistant: "Great! Let me review the code quality."
<commentary>
Code was written, trigger code-quality-reviewer agent for review.
</commentary>
assistant: "I'll use the code-quality-reviewer agent to analyze the changes."
</e

*(content truncated)*

## See Also

- [[template-post-run-agent-self-assessment]]
- [[azure-ai-foundry-agents-open-agent-skills]]
- [[azure-ai-foundry-open-agent-skill-integration-plan]]
- [[azure-ai-foundry-agents-open-agent-skills]]
- [[azure-ai-foundry-agents-open-agent-skills]]
- [[azure-ai-foundry-agents-open-agent-skills]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/examples/agent-creation-prompt.md`
- **Indexed:** 2026-04-17T06:42:09.997258+00:00
