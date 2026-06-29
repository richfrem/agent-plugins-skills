---
name: agy-cli-agent
plugin: cli-agents
description: >
  Antigravity (`agy`) CLI sub-agent system for all Google Gemini models and cross-model
  access (Gemini, Claude, GPT-OSS) via the agy binary. Use when dispatching tasks to
  Gemini 3.1 Pro (cheapest real-world), Gemini 3.5 Flash, or other agy-hosted models.
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

### Model Strategy: Use `gemini-3.1-pro` by Default

> **See `references/agy-models.json`** for the full model catalog, cost tiers, and strategy field.

```bash
# Default (cheapest real-world agentic cost)
python ./scripts/run_agent.py <PERSONA> <INPUT> <OUTPUT> "<INSTR>" --cli agy
# ↑ run_agent.py loads gemini-3.1-pro from references/cheapest_models.json

# Explicit model override
python ./scripts/run_agent.py <PERSONA> <INPUT> <OUTPUT> "<INSTR>" --cli agy --model gemini-3.1-pro
```

### Agentic Token Trap — Why Flash Costs 3–5× More

Gemini 3.5 Flash has a "Thought Preservation" feature that carries reasoning context forward
across turns. In multi-step CLI operations this **hyper-inflates input tokens** even at Low thinking:

| Model | List Price (in/out per 1M) | Avg Turns/Task | Avg Context/Task | Real Cost |
|:---|:---:|:---:|:---:|:---:|
| **Gemini 3.1 Pro (Low)** | $2.00 / $12.00 | ~26 | ~650K tokens | **1× (baseline)** |
| Gemini 3.5 Flash (Low) | $1.50 / $9.00 | ~39 | ~1.4M tokens | **3–5× more expensive** |

**Bottom line:** Flash looks cheaper on list price but is far more expensive per completed task.
Use `gemini-3.1-pro` for all CLI dispatch. Reserve Flash for single-shot or interactive sessions.

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

`run_agent.py` calls `agy --dangerously-skip-permissions -p` and streams output live to stdout and the output file simultaneously. Loads model from `references/cheapest_models.json` (currently `gemini-3.1-pro`).

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

| Display Name (agy models) | `--model` ID | Thinking | Rec |
|:---|:---|:---:|:---|
| **Gemini 3.1 Pro (Low)** | `gemini-3.1-pro` | Low | **Default — cheapest overall** |
| Gemini 3.1 Pro (High) | `gemini-3.1-pro-high` | High | Complex reasoning tasks |
| Gemini 3.5 Flash (Low) | `gemini-3.5-flash-low` | Low | Avoid in CLI loops |
| Gemini 3.5 Flash (Medium) | `gemini-3.5-flash` | Medium | Avoid — legacy default |
| Gemini 3.5 Flash (High) | `gemini-3.5-flash-high` | High | Avoid — max token burn |
| Claude Sonnet 4.6 (Thinking) | `claude-sonnet-4.6-thinking` | — | Anthropic quality via agy |
| Claude Opus 4.6 (Thinking) | `claude-opus-4.6-thinking` | — | Critical tasks only |
| GPT-OSS 120B (Medium) | `gpt-oss-120b` | Medium | OpenAI OSS via agy |

> Full pricing data and strategy field: `references/agy-models.json`

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
