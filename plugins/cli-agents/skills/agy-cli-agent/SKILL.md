---
name: agy-cli-agent
plugin: cli-agents
description: >
  Antigravity (`agy`) CLI sub-agent system for frontier Google Gemini models.
  Use when dispatching tasks to Gemini 3.5 Flash and above via the `agy` binary.
  For cheaper/older Gemini models (gemini-3-flash-preview, gemini-3.1-pro-preview),
  use gemini-cli-agent instead. Trigger with "use agy", "dispatch to antigravity",
  "run with agy", "use frontier gemini model", or "agy sub-agent".
allowed-tools: Bash, Read, Write
---

## Identity: The Antigravity Sub-Agent Dispatcher (Frontier: Gemini 3.5 Flash+)

You dispatch tasks to Google Gemini frontier models via the `agy` binary.

> [!IMPORTANT]
> `agy` is the Antigravity CLI for **frontier models only** (Gemini 3.5 Flash and above). It is a separate binary from `gemini`. For cost-efficient older models, use `gemini-cli-agent`.

### CLI Selection Rule

| Use case | CLI | Binary |
|:---|:---|:---|
| Frontier models (3.5 Flash+) | Antigravity | `agy` |
| Cheaper/older models (3-flash, 2.5-pro) | Gemini CLI | `gemini` |

---

## Minimal Working Pattern

```bash
agy --dangerously-skip-permissions -p "$(cat agents/persona.md)

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
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" --cli agy
```

`run_agent.py` calls `agy --dangerously-skip-permissions -p` and streams output live to stdout and the output file simultaneously.

### Health Check
```bash
agy -p "HEARTBEAT CHECK: Respond with HEARTBEAT_OK only."
# or via run_agent.py:
python ./scripts/run_agent.py /dev/null /dev/null ./heartbeat.md "HEARTBEAT CHECK: Respond HEARTBEAT_OK only." --cli agy
grep -q "HEARTBEAT_OK" ./heartbeat.md && echo "OK" || echo "FAIL"
```

### Example
```bash
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
"Find vulnerabilities. Use severity levels: 🔴 CRITICAL, 🟡 MODERATE, 🟢 MINOR." --cli agy
```

---

## Persona Registry (`agents/`)

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

---

## CLI Flags Reference

| Flag | Purpose |
|:---|:---|
| `-p "prompt"` / `--prompt "prompt"` | Pass prompt non-interactively |
| `--dangerously-skip-permissions` | Headless mode — skip all permission prompts |
| `--sandbox` | Run in sandboxed environment |

---

## CLI Best Practices

### Path
`agy` is typically at `/opt/homebrew/bin/agy`. Confirm with `which agy`.

### Avoid Shell Expansion for Large Contexts
`$(cat ...)` > 10KB can silently fail. `run_agent.py` writes to a temp file automatically.

### Backgrounding & TTY (SIGTTIN)
```bash
nohup agy --dangerously-skip-permissions -p "..." >> log.txt 2>&1 < /dev/null &
```
`< /dev/null` is required to prevent SIGTTIN stops in background processes.

---

## Smoke Test

```bash
agy -p "hello"
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code." --cli agy
```
