---
name: gemini-cli-agent
description: >
  Gemini CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to Google Gemini models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## Identity: The Gemini Sub-Agent Dispatcher 🎭

You, the Antigravity agent, dispatch specialized analysis tasks to Gemini CLI sub-agents. 

### ✅ Minimal Working Code Review Agent Pattern

To ensure Gemini CLI behaves as a specialized persona rather than a generic responder, **always** embed the persona and source material directly into the prompt flag (`-p`).

```bash
gemini -m gemini-3-flash-preview -p "$(cat agents/persona.md)

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
# Location: plugins/gemini-cli/scripts/run_agent.py
python3 ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>"
```

### Example Usage:
```bash
python3 ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
"Find vulnerabilities. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR."
```

---

## 🎭 Persona Registry (`agents/`)

These personas are mirrored from the Copilot CLI plugin to ensure consistent "Agentic" analysis across the ecosystem.

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

---

## ⚠️ CLI Best Practices & Failure Modes

### 1. ⚡ Preferred Model: Gemini 3 Flash
For analytical sub-agent tasks, **always** specify `-m gemini-3-flash-preview`. It provides the best balance of context window (1M+ tokens) and latency for analytical reviews.

### 2. ❌ Avoid Shell Expansion for Large Contexts
Large prompt expansions (e.g., `$(cat ...)` > 10KB) can silently fail when run in the background. 
- **Fix**: Use a temporary file for the combined prompt (as implemented in `run_agent.sh`).
- **Fix**: Run commands sequentially and verify output size with `wc -l`.

### 3. 🧩 Force Agent Behavior
Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

---

## 🔄 How to Update Gemini CLI
- **Via NPM (Global)**: Run `npm install -g @google/gemini-cli@latest`.
- **Via Brew (macOS/Linux)**: Run `brew upgrade gemini-cli`.
- **Using NPX**: Use `npx @google/gemini-cli` to automatically pull the latest version.

---

## ✅ Smoke Test

```bash
./plugins/gemini-cli/scripts/run_agent.sh agents/refactor-expert.md target.py output.md "Refactor this code."
```
