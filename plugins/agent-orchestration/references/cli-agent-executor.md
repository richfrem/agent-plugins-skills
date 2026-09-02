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

You, the Antigravity agent, dispatch specialized analysis tasks to the CLI sub-agents natively supported by this ecosystem (claude-cli, agy-cli, copilot-cli).

## 🛠️ Core Pattern
```bash
# Recommended: Run via run_agent.py multi-LLM router
python scripts/run_agent.py <PERSONA_PROMPT> <INPUT> <OUTPUT> "<INSTRUCTION>" --cli agy

# Direct execution (using file-ref system prompt and stdin redirection):
agy --dangerously-skip-permissions -p "$(cat <PERSONA_PROMPT>)" < <INPUT> > <OUTPUT>
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
# With a system prompt file (running via run_agent.py router):
python scripts/run_agent.py system_prompt.md pr.md review.md "Review this PR" --cli claude

# Without a system prompt (general-purpose direct execution):
claude -p "Analyze this code for security issues" < input.md > analysis.md

# Antigravity (agy) equivalent:
python scripts/run_agent.py system_prompt.md bundle.md audit.md "Audit this architecture" --cli agy
```

## 🔄 Recommended Audit Loop

When asked to perform a comprehensive "Audit Loop", construct a sequence of CLI dispatches
passing the SAME `bundle.md` or context block to consecutive specialist prompts.

1. **Security Review**
   `python scripts/run_agent.py security_prompt.md bundle.md audit_01_security.md "ACT AS SECURITY AUDITOR. Focus on vulnerabilities." --cli agy`

2. **Architecture Review**
   `python scripts/run_agent.py architect_prompt.md bundle.md audit_02_architecture.md "ACT AS ARCHITECT REVIEWER. Focus on patterns and complexity." --cli agy`

3. **QA Review**
   `python scripts/run_agent.py qa_prompt.md bundle.md audit_03_qa.md "ACT AS QA EXPERT. Focus on testability and edge cases." --cli agy`

Always run the Architect **AFTER** the Security review to catch any security-driven side effects
that may have artificially inflated the system's complexity.
