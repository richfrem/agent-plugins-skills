---
name: cli-agent-executor
description: >
  CLI Sub-Agent System (Claude, Gemini, Copilot) for persona-based analysis. Use when piping
  large contexts to LLM CLI models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
---

## Ecosystem Role: Inner Loop Specialist

This reference describes specialized **Inner Loop Execution** patterns for the [`dual-loop`](../skills/dual-loop/SKILL.md) skill.

- **Orchestrated by**: [`orchestrator`](../skills/orchestrator/SKILL.md)
- **Use Case**: When "generic coding" is insufficient and specialized expertise (Security, QA, Architecture) is required.
- **Why**: The CLI context is naturally isolated (no git, no tools), making it the perfect "Safe Inner Loop".

## Identity: The Sub-Agent Dispatcher 🎭

You, the Antigravity agent, dispatch specialized analysis tasks to the CLI sub-agents natively supported by this ecosystem (claude-cli, gemini-cli, copilot-cli).

## 🛠️ Core Pattern
```bash
cat <PERSONA_PROMPT> | <CLI_ENGINE> -p "<INSTRUCTION>" < <INPUT> > <OUTPUT>
```

## ⚠️ CLI Best Practices

### 1. Token Efficiency — PIPE, Don't Load
**Bad** — loads file into agent memory just to pass it:
```python
content = read_file("large.log")
run_command(f"<cli_engine> -p 'Analyze: {content}'")
```
**Good** — direct shell piping:
```bash
<cli_engine> -p "Analyze this log" < large.log > analysis.md
```

### 2. Self-Contained Prompts
The CLI runs in a **separate context** — no access to agent tools or memory.
- **Add**: "Do NOT use tools. Do NOT search filesystem."
- Ensure prompt + piped input contain 100% of necessary context

### 3. Output to File
Always redirect output to a file (`> output.md`), then review with `view_file`.

## 🎭 Specialization via System Prompts

Specialized behavior is achieved by passing a system prompt file to the CLI agent. The source
of that system prompt is up to you — user-supplied, from an installed persona plugin
(e.g., `agent-personas`), or inline in the command.

```bash
# With a system prompt file:
cat system_prompt.md | claude -p "Review this PR" < pr.md > review.md

# Without a system prompt (general-purpose):
claude -p "Analyze this code for security issues" < input.md > analysis.md

# Gemini equivalent:
cat system_prompt.md | gemini -p "Audit this architecture" < bundle.md > audit.md
```

## 🔄 Recommended Audit Loop

When asked to perform a comprehensive "Audit Loop", construct a sequence of CLI dispatches
passing the SAME `bundle.md` or context block to consecutive specialist prompts.

1. **Security Review**
   `cat security_prompt.md | claude -p "ACT AS SECURITY AUDITOR. Do NOT use tools." < bundle.md > audit_01_security.md`

2. **Architecture Review**
   `cat architect_prompt.md | claude -p "ACT AS ARCHITECT REVIEWER. Focus on complexity and patterns. Do NOT use tools." < bundle.md > audit_02_architecture.md`

3. **QA Review**
   `cat qa_prompt.md | claude -p "ACT AS QA EXPERT. Focus on testability and edge cases. Do NOT use tools." < bundle.md > audit_03_qa.md`

Always run the Architect **AFTER** the Security review to catch any security-driven side effects
that may have artificially inflated the system's complexity.
