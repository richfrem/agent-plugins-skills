---
concept: agent-triggering-examples-best-practices
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/triggering-examples.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.018665+00:00
cluster: plugin-code
content_hash: 2a5ea013c97fc9f2
---

# Agent Triggering Examples: Best Practices

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Triggering Examples: Best Practices

Complete guide to writing effective `<example>` blocks in agent descriptions for reliable triggering.

## Example Block Format

The standard format for triggering examples:

```markdown
<example>
Context: [Describe the situation - what led to this interaction]
user: "[Exact user message or request]"
assistant: "[How Claude should respond before triggering]"
<commentary>
[Explanation of why this agent should be triggered in this scenario]
</commentary>
assistant: "[How Claude triggers the agent - usually 'I'll use the [agent-name] agent...']"
</example>
```

## Anatomy of a Good Example

### Context

**Purpose:** Set the scene - what happened before the user's message

**Good contexts:**
```
Context: User just implemented a new authentication feature
Context: User has created a PR and wants it reviewed
Context: User is debugging a test failure
Context: After writing several functions without documentation
```

**Bad contexts:**
```
Context: User needs help (too vague)
Context: Normal usage (not specific)
```

### User Message

**Purpose:** Show the exact phrasing that should trigger the agent

**Good user messages:**
```
user: "I've added the OAuth flow, can you check it?"
user: "Review PR #123"
user: "Why is this test failing?"
user: "Add docs for these functions"
```

**Vary the phrasing:**
Include multiple examples with different phrasings for the same intent:
```
Example 1: user: "Review my code"
Example 2: user: "Can you check this implementation?"
Example 3: user: "Look over my changes"
```

### Assistant Response (Before Triggering)

**Purpose:** Show what Claude says before launching the agent

**Good responses:**
```
assistant: "I'll analyze your OAuth implementation."
assistant: "Let me review that PR for you."
assistant: "I'll investigate the test failure."
```

**Proactive example:**
```
assistant: "Great! Now let me review the code quality."
<commentary>
Code was just written, proactively trigger review agent.
</commentary>
```

### Commentary

**Purpose:** Explain the reasoning - WHY this agent should trigger

**Good commentary:**
```
<commentary>
User explicitly requested code review, trigger the code-reviewer agent.
</commentary>

<commentary>
After code implementation, proactively use review agent to check quality.
</commentary>

<commentary>
PR analysis request matches pr-analyzer agent's expertise.
</commentary>
```

**Include decision logic:**
```
<commentary>
User wrote tests (Test tool used). The test-analyzer agent should check
test quality and coverage before continuing.
</commentary>
```

### Assistant Response (Triggering)

**Purpose:** Show how Claude invokes the agent

**Standard pattern:**
```
assistant: "I'll use the [agent-name] agent to [what it will do]."
```

**Examples:**
```
assistant: "I'll use the code-reviewer agent to analyze the changes."
assistant: "Let me use the test-generator agent to create comprehensive tests."
assistant: "I'll use the security-analyzer agent to check for vulnerabilities."
```

## Example Types

### Type 1: Explicit Request

User directly asks for what the agent does:

```markdown
<example>
Context: User explicitly requests security analysis
user: "Check my code for security vulnerabilities"
assistant: "I'll use the security-analyzer agent to perform a thorough security review."
<commentary>
Direct security analysis request triggers the security-analyzer agent.
</commentary>
</example>
```

### Type 2: Proactive Triggering

Agent triggers after relevant work without explicit request:

```markdown
<example>
Context: User just implemented database queries
user: "I've added the user search functionality"
assistant: "Great! Let me review it for security."
<commentary>
Database code written. Proactively trigger security-analyzer to check
for SQL injection and other database security issues.
</commentary>
assistant: "I'll use the security-analyzer agent to check the database code."
</example>
```

### Type 3: Implicit Request


*(content truncated)*

## See Also

- [[agent-skills-best-practices]]
- [[agent-skills-best-practices]]
- [[complete-agent-examples]]
- [[complete-agent-examples]]
- [[triggering-examples]]
- [[link-checking-standards-best-practices]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/triggering-examples.md`
- **Indexed:** 2026-04-17T06:42:10.018665+00:00
