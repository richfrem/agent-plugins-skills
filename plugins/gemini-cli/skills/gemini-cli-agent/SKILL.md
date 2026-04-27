---
name: gemini-cli-agent
plugin: gemini-cli
description: >
  Gemini CLI sub-agent system for persona-based analysis. Use when piping
  large contexts to Google Gemini models for security audits, architecture reviews,
  QA analysis, or any specialized analysis requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## 🎭 Identity: The Gemini Sub-Agent Dispatcher (Standard: gemini-3-flash-preview)

You, the Antigravity agent, dispatch specialized analysis tasks to Gemini CLI sub-agents. 

> [!IMPORTANT]
> By default, all Gemini sub-agent orchestration uses the **gemini-3-flash-preview** model for maximum cost-efficiency. For deep analytical reasoning, structural validation, or multimodal vision tasks, explicitly override the model to **gemini-3.1-pro-preview**.

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
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" [MODEL_NAME]
```

### 🧪 Mandatory Validation Protocol (Phase 0.5)
Before using Gemini in any autonomous Triple-Loop or complex orchestration, you **must** verify the CLI's and the orchestrator's health:
1. **Hello Check**: `gemini --yolo -m gemini-3-flash-preview -p "hello"`
2. **Functional Check**: `python ./scripts/run_agent.py agents/refactor-expert.md target.py ./HEARTBEAT_MD.md "Verify health"`
3. **Verify Output**: Confirm `./HEARTBEAT_MD.md` is not empty.

### Example Usage:
```bash
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
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

## 🚫 Capability Boundary — Read Before Dispatching

### ❌ Image Generation is NOT supported via Gemini CLI
The Gemini CLI (`gemini` binary) is a **text and code assistant only**. It cannot generate, render, or save image files regardless of model.

- `gemini-3.1-pro-preview`, `gemini-2.5-pro`, `gemini-3-flash-preview` — **text only**
- Asking the CLI to "generate an image and save it" will always fail or hallucinate
- Image generation models (`imagen-4.0-*`, `gemini-2.5-flash-image`, `gemini-3-pro-image-preview`) are **not accessible via the CLI** — they require the Python `google-genai` SDK with a **paid billing account** (separate from Gemini Pro subscription)
- `gemini-3.1-pro-preview` may hit `MODEL_CAPACITY_EXHAUSTED` (429) under load — retry or fall back to `gemini-2.5-pro`

**Do not attempt image generation via this skill. Inform the user immediately.**

---

## ⚠️ CLI Best Practices & Failure Modes

### 1. ⚡ Preferred Model: Gemini 3 Flash
For analytical sub-agent tasks where cost is prioritized, **always** specify `-m gemini-3-flash-preview`. For deep reasoning or validation, use `-m gemini-3.1-pro-preview`.

### 2. ❌ Avoid Shell Expansion for Large Contexts
Large prompt expansions (e.g., `$(cat ...)` > 10KB) can silently fail when run in the background. 
- **Fix**: Use a temporary file for the combined prompt (as implemented in `run_agent.py`).
- **Fix**: Run commands sequentially and verify output size with `wc -l`.

### 3. 🧩 Force Agent Behavior
Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

### 4. 🚀 Autonomous Triple-Loop Orchestration (`--yolo`)
If you are deploying Gemini CLI as an active orchestrator (e.g., an L1 Evaluator running an improvement loop), pass the `--yolo` flag. This allows all tool calls (like bash commands or Python execution) to run automatically without manual confirmation, enabling fully headless sub-agent operation.

### 5. 🛑 Workspace Boundaries (IDEClient Directory Mismatch)
The `gemini` CLI inherits strict workspace bounds. If you `cd` into an external directory (e.g., a test lab repo) and attempt to invoke `gemini` from there, it will crash with `[ERROR] [IDEClient] Directory mismatch`.
- **Fix:** *Always* invoke `gemini` from your active OS workspace directory. If you need the sub-agent to operate in an external folder, pass instructions in the prompt string telling it to `cd` into that folder itself (e.g., `gemini --yolo -p "Use bash to cd to /external/lab/repo first, then..."`).

### 6. 🛡️ Backgrounding & TTY (SIGTTIN)
When running `gemini` or `copilot` in a background shell (e.g. `&`), it may be **stopped** by the OS (STP status) if it attempts to interact with the TTY.
- **Fix**: Use `nohup` and detach from `stdin`:
```bash
nohup gemini --yolo -m gemini-3-flash-preview -p "..." >> log.txt 2>&1 < /dev/null &
```
- **Fix**: Redirection `< /dev/null` is critical to prevent `SIGTTIN` blocks.
- **Fix**: If you see `Tool execution denied by policy`, ensure the directory has been added to `gemini trust`.

---

## 🔄 How to Manage Gemini CLI
- **Update CLI**: Run `npm install -g @google/gemini-cli@latest`.
- **Install Plugin Suite**: Run `gemini extensions install https://github.com/richfrem/agent-plugins-skills`.
- **Using NPX**: Use `npx @google/gemini-cli` to automatically pull the latest version.

---

## ✅ Smoke Test

```bash
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```
