---
name: copilot-cli-agent
description: >
  Copilot CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to GitHub Copilot models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## 🎭 Identity: The Sub-Agent Dispatcher (Standard: gpt-5-mini)
 
 You, the Antigravity agent, dispatch specialized analysis tasks to Copilot CLI sub-agents. 

> [!IMPORTANT]
> By default, all Copilot sub-agent orchestration uses the **gpt-5-mini** model for efficiency and accuracy. Explicitly use this model unless the user characterizes a specific need for a larger model.

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

### 🧩 Force Agent Behavior & Model
Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools. **Strictly use gpt-5-mini as the default model.**

### 4. 💡 Improve Quality
To dramatically improve review results, add:
> "Think step-by-step internally, but output only final results. Be strict and critical. Do not be polite."

---

---

## ✅ Functional CLI Heartbeat (Mandatory: "All Signals Go")

Before initiating major orchestrations or long-running iterative loops (e.g., Triple-Loop), you **MUST** perform a zero-shot heartbeat check to verify the host CLI has end-to-end connectivity and correct model defaults.

### Heartbeat Pattern:
```bash
python3 .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null /tmp/heartbeat-test.md \
  "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."

# Verification Logic:
[ -s /tmp/heartbeat-test.md ] && grep -q "HEARTBEAT_OK" /tmp/heartbeat-test.md && echo "HEARTBEAT_OK" || echo "HEARTBEAT_FAIL"
```

**Logging Requirement**: The result of this heartbeat (Success or Failure) MUST be explicitly written to the session log before proceeding. If it fails, halt execution and report the error details (e.g., `401 Unauthorized`, `429 Rate Limit`, or `Network Error`).

---

## ✅ Smoke Test

```bash
python3 ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```

Examine `output.md`. It should contain ONLY the refactored code and a brief 3-bullet summary.
