---
name: copilot-cli-agent
description: >
  Copilot CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to GitHub Copilot models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## Identity: The Sub-Agent Dispatcher 🎭

You, the Antigravity agent, dispatch specialized analysis tasks to Copilot CLI sub-agents. 

### ✅ Minimal Working Code Review Agent Pattern

To ensure Copilot CLI behaves as a specialized persona rather than a generic responder, **always** embed the persona and source material directly into the prompt flag (`-p`).

```bash
copilot -p "$(cat agents/persona.md)

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
# Location: plugins/copilot-cli/scripts/run_agent.py
python3 ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>"
```

### Example Usage:
```bash
python3 ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
"Find vulnerabilities. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR."
```

---

## 🎭 Persona Registry (`agents/`)

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

---

## ⚠️ CLI Best Practices & Failure Modes

### 1. ❌ Why Stdin Piping Fails
Using `cat code.py | copilot -p "review this"` is unreliable. The CLI often prioritizes the prompt flag and ignores the piped input. **Always embed the code** inside the command string as shown in the Core Pattern.

### 2. ❌ Empty Output (Background Runs)
Large prompt expansions (e.g., `$(cat ...)` > 10KB) can silently fail when run in the background (`&`). 
- **Fix**: Use a temporary file for the combined prompt (as implemented in `run_agent.py`).
- **Fix**: Run commands sequentially and verify output size with `wc -l`.

### 3. 🧩 Force Agent Behavior
Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

### 4. 💡 Improve Quality
To dramatically improve review results, add:
> "Think step-by-step internally, but output only final results. Be strict and critical. Do not be polite."

---

## ✅ Smoke Test

```bash
python3 ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```

Examine `output.md`. It should contain ONLY the refactored code and a brief 3-bullet summary.
