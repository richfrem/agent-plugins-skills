---
name: agy-cli-agent
plugin: cli-agents
description: >
  Antigravity (`agy`) CLI sub-agent system for all Google Gemini models and cross-model
  access (Gemini, Claude, GPT-OSS) via the agy binary. Use when dispatching tasks to
  Gemini 3.1 Pro, Gemini 3.8 Flash, or other agy-hosted models.
  Replaces the deprecated gemini-cli-agent (gemini binary retired June 18 2026).
  Trigger with "use agy", "dispatch to antigravity", "run with agy", "use gemini model",
  "agy sub-agent", or "use cheapest gemini".
allowed-tools: Bash, Read, Write
---

## Execution Contract

> **See `references/execution-contract.md` (full rules) and `references/backend-capabilities.md` (backend selection).**
>
> Key rules: (1) One backend per task — no silent fallback. (2) Run `output-validator` or
> `self-critic` when output quality is uncertain. (3) Architecture/high-risk tasks require
> `architect-review` → `red-team-reviewer` → `debate-synthesizer`. (4) Backend failure →
> halt and log to `references/map-debt.md`. No workarounds.

---

## Identity: The Antigravity Sub-Agent Dispatcher

You dispatch tasks to Google Gemini (and other) models via the `agy` binary.

> [!IMPORTANT]
> `agy` is the **sole Gemini CLI** since the standalone `gemini` binary retired June 18 2026.
> All Gemini model work — including cost-efficient older models — routes through `agy`.

## Native orchestration facilities (verified September 2026)

`agy` has a native `--mode=plan` that investigates with read-only tools and presents an
outline before edits. It also has asynchronous background subagents, custom agent profiles,
and a `/agents` panel. Use them for genuinely independent work; keep a single agent for a
small, coupled edit. The CLI does **not** document a flag that creates or manages Git
worktrees, so create the governed portable worktree first and invoke `agy` inside it.

```bash
# Plan without editing
agy --mode=plan -p "Inspect this repository and propose an implementation plan."

# Inspect locally installed custom agents before selecting one
agy agents
```

Do not treat `--dangerously-skip-permissions` as isolation: it approves tool requests. Use
`--sandbox` for terminal restrictions, and retain the control plane's approval and receipt
requirements even when agy delegates work.

### Model Strategy: Flash by Default, Pro for Deep Reasoning

> **See `references/agy-models.json`** for the full model catalog, cost tiers, and strategy field.

```bash
# Default (Flash — faster, cheaper/token, optimized for agentic/coding tasks)
python ./scripts/run_agent.py <PERSONA> <INPUT> <OUTPUT> "<INSTR>" --cli agy
# ↑ run_agent.py loads the current Flash model from references/cheapest_models.json

# Explicit Low effort (recommended for CLI loops to control Thought Preservation cost)
python ./scripts/run_agent.py <PERSONA> <INPUT> <OUTPUT> "<INSTR>" --cli agy --model gemini-3.8-flash --effort low

# Pro — escalate for deep reasoning / architecture decisions
python ./scripts/run_agent.py <PERSONA> <INPUT> <OUTPUT> "<INSTR>" --cli agy --model gemini-3.1-pro
```

### Flash vs Pro: Which to Use

| | **Gemini 3.8 Flash** | **Gemini 3.1 Pro** |
|:---|:---:|:---:|
| Price (in/out per 1M, through 2026-12-31) | $0.75 / $3.75 | $2.00 / $12.00 |
| Speed | Not benchmarked | Not benchmarked |
| Agentic tool use / MCP / terminal | **Best** | Good |
| Coding (edit-test loops) | **Best** | Better for final review |
| Deep abstract reasoning | Good | **Best** |
| Architecture planning | Good | **Best** |
| Max output tokens | **65,536** | 32,768 |

**Default: Flash.** Use Pro only when the task requires deep multi-step reasoning or expert-level judgment.

> **Thinking level note:** Flash with High thinking can inflate tokens via Thought Preservation.
> Use Low thinking level for high-frequency CLI dispatch loops.

---

## Minimal Working Pattern

```bash
agy --dangerously-skip-permissions --model "Gemini 3.1 Pro (Low)" -p "$(cat agents/persona.md)

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

For medium or high reasoning, pass the effort explicitly (the wrapper also maps
`--tier` to effort for agy when `--effort` is omitted):

```bash
python ./scripts/run_agent.py agents/architect-review.md plan.md output.md "Review the plan." \
  --cli agy --model gemini-3.8-flash --tier medium --effort medium --isolated
```

The shared router validates `low|medium|high` and forwards a non-empty `--effort` to `agy`.
When `--model` is explicit and `--effort` is omitted, it derives effort from `--tier`.
Verify the assembled command or run a heartbeat before an expensive dispatch.

### Print-mode timeout

`agy --print` defaults to a **5-minute** wait (`--print-timeout 5m0s`). Set the timeout
explicitly for bounded implementation work; for example, use `--print-timeout 15m0s` when
the approved task allows up to 15 minutes. This controls the CLI wait window, not model
quality or quota. If the timeout is omitted, a valid long-running task may be terminated
before it reports a commit.

`run_agent.py` calls `agy --dangerously-skip-permissions -p` and streams output live to stdout and the output file simultaneously. Loads model from `references/cheapest_models.json` (currently `gemini-3.8-flash-low`).

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

## Available Models

`update-cli-models` is the sole authority for current Agy model IDs, picker
availability, pricing, and synchronized catalog copies. Read
`references/agy-models.json` through that authority before selecting a model;
effort is selected separately from the model. The current picker choices are
represented in that catalog, including Gemini 3.8/3.7/3.6 Flash, Gemini 3.1
Pro, Claude Sonnet/Opus 4.6 Thinking, and GPT-OSS 120B.

> Full pricing data and strategy field: `references/agy-models.json`

---

## 🎭 Persona Registry (`agents/`)

These personas are mirrored across CLI agent dispatchers to ensure consistent analytical behavior across the ecosystem.

| Persona | Use For |
|:---|:---|
| `security-auditor.md` | Red team, vulnerability scanning, threat modeling |
| `refactor-expert.md` | Optimizing code for readability, performance, and DRY |
| `architect-review.md` | Assessing system design, modularity, and complexity |

### 🧩 Force Agent Behavior

Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

### 🛠️ Orchestration Pattern: `run_agent.py` (Cross-Platform)

For reusable sub-agent execution, use the provided Python orchestrator which handles temp file assembly and prompt concatenation reliably across Windows, macOS, and Linux:

```bash
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>"
```

---

## CLI Flags Reference

| Flag | Purpose |
|:---|:---|
| `-p "prompt"` / `--prompt "prompt"` | Pass prompt non-interactively |
| `--model <id>` | Select model (see table above) |
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
