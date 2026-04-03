---
name: gemini-cli-agent
description: >
  Gemini CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to Google Gemini models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
## Ecosystem Role: Inner Loop Specialist

This skill provides specialized **Inner Loop Execution** for the `dual-loop` skill.

- **Orchestrated by**: the `agent-orchestrator` skill (see the dual-loop plugin)
- **Use Case**: When "generic coding" is insufficient and specialized expertise (Security, QA, Architecture) is required.
- **Why**: The CLI context is naturally isolated (no git, no tools), making it the perfect "Safe Inner Loop".

## Identity: The Sub-Agent Dispatcher 🎭

You, the Antigravity agent, dispatch specialized analysis tasks to Gemini CLI sub-agents.

## 🛠️ Core Pattern
```bash
cat <PERSONA_PROMPT> | gemini -p "<INSTRUCTION>" < <INPUT> > <OUTPUT>
```
*Note: Gemini uses `-p` or `--prompt` for headless execution where output is desired without interactive prompts.*

### ⚠️ Large Context: Prefer Stdin Piping
For large files, use stdin piping rather than `$(cat ...)` shell expansion.
Shell expansion in background jobs (`&`) with large prompts silently produces empty output:
```bash
# Good — stdin pipe (works reliably for large files)
cat combined_prompt_and_content.txt | gemini -p "Apply the rules in this document. Output the fixed file only." > /tmp/output.md

# Alternatively — build temp file then run sequentially (not in background)
cat prompt.md > /tmp/combined.txt && cat target.md >> /tmp/combined.txt
gemini -p "$(cat /tmp/combined.txt)" > /tmp/output.md
```
**Gemini Flash limits (as of 2026):**
- Context window: 1,048,576 tokens (~50k lines of code)
- Max output: 65,536 tokens
- Rate limit: ~1,500 requests/day, ~15 RPM on free tier
- Concurrency: treat as 1 request every 4 seconds to stay safe
- Model flag: `-m flash` or `-m gemini-3.1-flash` for explicit Flash selection

**Known issue**: Running gemini in background (`&`) with large `$(cat ...)` prompts produces empty output.
Always run sequentially and verify: `wc -l /tmp/output.md` before applying changes.

## ⚠️ CLI Best Practices

### 1. Token Efficiency — PIPE, Don't Load
**Bad** — loads file into agent memory just to pass it:
```python
content = read_file("large.log")
run_command(f"gemini -p 'Analyze: {content}'")
```
**Good** — direct shell piping:
```bash
gemini -p "Analyze this log" < large.log > analysis.md
```

### 2. Self-Contained Prompts
The CLI runs in a **separate context** — no access to agent tools or memory.
- **Add**: "Do NOT use tools. Do NOT search filesystem."
- Ensure prompt + piped input contain 100% of necessary context.
- **Model Selection**: Gemini supports the `-m <model>` flag (e.g., `-m gemini-3.1-pro-preview`, `-m gemini-2.5-pro`, or alias `-m flash-lite`).

### 3. Output to File
Always redirect output to a file (`> output.md`), then review with `view_file`.

### 4. Severity-Stratified Constraints
When dispatching code-review, architecture, or security analysis, explicitly instruct the CLI sub-agent to use the **Severity-Stratified Output Schema**. This ensures the Outer Loop can parse the results deterministically:
> "Format all findings using the strict Severity taxonomy: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR."

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

All personas are documented in the table above. Load the persona prompt file from your CLI plugin's `agents/` directory.

## 🔄 Recommended Audit Loop
1. **Red Team** (Security Auditor) → find exploits
2. **Architect** → validate design didn't add complexity
3. **QA Expert** → find untested edge cases

Run architect **AFTER** red team to catch security-fix side effects.
