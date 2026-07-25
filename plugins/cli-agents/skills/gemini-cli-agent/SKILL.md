---
name: gemini-cli-agent
plugin: cli-agents
description: >
  Gemini CLI sub-agent system for cost-efficient analysis using the `gemini` binary.
  Use when piping large contexts to cheaper Google Gemini models (gemini-3-flash-preview,
  gemini-3.1-pro-preview) for security audits, architecture reviews, or QA analysis.
  For frontier models (Gemini 3.5 Flash and above), use agy-cli-agent instead.
allowed-tools: Bash, Read, Write
---

> [!WARNING]
> **Gemini CLI consumer access ended June 18, 2026.** Free, Pro, and Ultra users no longer have access. Only enterprise Gemini Code Assist Standard/Enterprise licenses retain the `gemini` binary. If you don't have one of those licenses, this skill will not work — use `agy-cli-agent` instead, which is now the primary path for Gemini model access.

## Identity: The Gemini Sub-Agent Dispatcher (Standard: gemini-3-flash-preview)

You dispatch specialized analysis tasks to Gemini CLI sub-agents using the `gemini` binary.

> [!IMPORTANT]
> Default model: **gemini-3-flash-preview** (cost-efficient). For deep reasoning, use **gemini-3.1-pro-preview**. For frontier models (Gemini 3.5 Flash+), use `agy-cli-agent` instead.

### Minimal Working Pattern

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

## Orchestration Pattern: `run_agent.py`

```bash
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" [MODEL_NAME]
```

### Mandatory Health Check
Before any complex orchestration:
1. `gemini --yolo -m gemini-3-flash-preview -p "hello"`
2. `python ./scripts/run_agent.py agents/refactor-expert.md target.py ./heartbeat.md "Verify health"`
3. Confirm `./heartbeat.md` is not empty.

### Example
```bash
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
"Find vulnerabilities. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR."
```

---

## Persona Registry (`agents/`)

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

---

## Capability Boundary

### Image Generation NOT supported
The `gemini` binary is **text and code only**. Image generation models require the Python `google-genai` SDK with a paid billing account.

### Model Capacity
`gemini-3.1-pro-preview` may hit `MODEL_CAPACITY_EXHAUSTED` (429) under load — retry or fall back to `gemini-2.5-pro`.

---

## CLI Best Practices

### Avoid Shell Expansion for Large Contexts
`$(cat ...)` > 10KB can silently fail in background processes. Use `run_agent.py` which writes to a temp file.

### Autonomous Orchestration (`--yolo`)
Pass `--yolo` to allow all tool calls to run without confirmation for headless operation.

### Workspace Boundary (IDEClient Directory Mismatch)
Always invoke `gemini` from your active workspace directory. To operate in an external folder, pass a `cd` instruction in the prompt itself.

### Backgrounding & TTY (SIGTTIN)
```bash
nohup gemini --yolo -m gemini-3-flash-preview -p "..." >> log.txt 2>&1 < /dev/null &
```
`< /dev/null` is critical to prevent SIGTTIN stops.

### Update / Install
```bash
npm install -g @google/gemini-cli@latest
# or via npx (run_agent.py falls back to this automatically)
npx @google/gemini-cli
```

---

## Smoke Test

```bash
gemini -p "hello"
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```
