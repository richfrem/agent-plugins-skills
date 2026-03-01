---
name: cli-agent-executor
description: >
  CLI Sub-Agent System (Claude, Gemini, Copilot) for persona-based analysis. Use when piping
  large contexts to LLM CLI models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
---

## Ecosystem Role: Inner Loop Specialist

This reference describes specialized **Inner Loop Execution** patterns for the [`dual-loop`](../dual-loop/SKILL.md) skill.

- **Orchestrated by**: [`orchestrator`](../orchestrator/SKILL.md)
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

## 🎭 Persona Categories

| Category | Personas | Use For |
|:---|:---|:---|
| Security | security-auditor | Red team, vulnerability scanning |
| Development | 14 personas | Backend, frontend, React, Python, Go, etc. |
| Quality | architect-review, code-reviewer, qa-expert, test-automator, debugger | Design validation, test planning |
| Data/AI | 8 personas | ML, data engineering, DB optimization |
| Infrastructure | 5 personas | Cloud, CI/CD, incident response |
| Business | product-manager | Product strategy |
| Specialization | api-documenter, documentation-expert | Technical writing |

All personas are physically located inside their respective CLI plugin directories (e.g., `plugins/claude-cli/personas/`, `plugins/gemini-cli/personas/`). Use standard `/ls` equivalents to find the exact markdown file needed for your pipeline.

## 🔄 Recommended Audit Loop
When asked to perform a comprehensive "Audit Loop", you should construct a sequence of CLI dispatches passing the SAME `bundle.md` or context code block to three consecutive personas.

1. **Red Team**
   `cat plugins/claude-cli/personas/security/security-auditor.md | claude -p "ACT AS THE SECURITY AUDITOR. Do NOT use tools. Do NOT search filesystem." < bundle.md > audit_01_security.md`
   
2. **Architect**
   `cat plugins/claude-cli/personas/quality-testing/architect-review.md | claude -p "ACT AS THE ARCHITECT REVIEWER. Focus on complexity, patterns, scalability. Do NOT use tools." < bundle.md > audit_02_architecture.md`
   
3. **QA Expert**
   `cat plugins/claude-cli/personas/quality-testing/qa-expert.md | claude -p "ACT AS THE QA EXPERT. Focus on testability and edge cases. Do NOT use tools." < bundle.md > audit_03_qa.md`

Always run the Architect **AFTER** the Red Team to catch any security-driven side effects that may have artificially inflated the system's complexity.
