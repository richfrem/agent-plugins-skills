---
name: claude-cli-agent
plugin: cli-agents
description: >
  Claude CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to Anthropic models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## Identity: The Claude Sub-Agent Dispatcher 🎭

You, the Antigravity agent, dispatch specialized analysis tasks to Claude CLI sub-agents. 

## Native orchestration facilities (verified September 2026)

Claude Code provides native plan permission mode, native git worktree sessions (`--worktree`),
and managed background agents (`--bg`, `claude agents`, `attach`, `logs`, `stop`, and `rm`).
Use its worktree session when Claude Code is the active implementation runtime; otherwise keep
the portable `git worktree` path as the interoperable fallback. Custom agents can be supplied
with `--agent`/`--agents`.

```bash
# Plan before edits
claude --permission-mode plan "Analyze this change and write an implementation plan."

# Create an isolated Claude Code worktree session
claude --worktree p0-observability-foundation "Implement the approved plan."
```

Native autonomy is not approval to bypass governance. `--dangerously-skip-permissions` is
appropriate only in an externally sandboxed, explicitly authorized execution environment.
Record the actual agents, model, effort, scope, and start time after dispatch.

### ✅ Minimal Working Code Review Agent Pattern

To ensure Claude CLI behaves as a specialized persona rather than a generic responder, **always** embed the persona and source material directly into the prompt flag (`-p`).

```bash
claude --model claude-haiku-4-5 -p "$(cat agents/persona.md)

---SOURCE CODE---
$(cat target.py)

---INSTRUCTION---
Perform a full code review. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR.
You are operating as an isolated sub-agent.
Do NOT use tools. Do NOT access filesystem." > review.md
```

---

## 🛠️ Orchestration Pattern: `run_agent.py` (Cross-Platform)

For reusable sub-agent execution, use the provided Python orchestrator which handles temp file assembly and prompt concatenation reliably across Windows, macOS, and Linux.

```bash
# Location: plugins/cli-agents/scripts/run_agent.py
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>"
```

### Example Usage:
```bash
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
"Find vulnerabilities. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR."
```

---

## 🎭 Persona Registry (`agents/`)

These personas are mirrored from the Gemini and Copilot plugins to ensure consistent "Agentic" analysis across the ecosystem.

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

---

## ⚠️ CLI Best Practices & Failure Modes

### 1. ⚡ Preferred Model: Claude Haiku 4.5
For rapid, cost-effective analytical sub-agent tasks, specify `--model claude-haiku-4-5`. This is the direct Claude CLI model identifier for the lowest-cost current Claude model.

### 2. ❌ Leading Newline Fix
If your prompt starts with YAML frontmatter (e.g., `---`), some shell parsers might misinterpret the flag. **Always prepend a newline** to the prompt string when passing it to `-p`. (Note: The `run_agent.py` script handles this automatically).

### 3. 🧩 Force Agent Behavior
Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

---

## ✅ Smoke Test

```bash
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```

For mandatory review source, pass `--require-input` to `run_agent.py`; missing or empty files
are rejected before backend dispatch. Supplied source is delimited with `---SOURCE---` and
`---END SOURCE---`. Record reviews with the control-plane `record-critic-review` command using
`PASS`, `REVISE`, or `REJECT`; `REQUEST_CHANGES` is normalized to `REVISE`, and only `PASS`
qualifies as an approval verdict.
