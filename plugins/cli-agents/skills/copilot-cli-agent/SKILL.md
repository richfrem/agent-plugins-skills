---
name: copilot-cli-agent
plugin: cli-agents
description: >
  Copilot CLI sub-agent system for dispatching tasks and persona-based analysis to
  GitHub Copilot models. Use for task delegation (agent reads/writes files directly),
  security audits, architecture reviews, or any work requiring a fresh model context.
allowed-tools: Bash, Read, Write
---

## ⚖️ Execution Contract

> **See `references/execution-contract.md` (full rules) and `references/backend-capabilities.md` (backend selection).**
>
> Key rules: (1) One backend per task — no silent fallback. (2) Run `output-validator` or
> `self-critic` when output quality is uncertain. (3) Architecture/high-risk tasks require
> `architect-review` → `red-team-reviewer` → `debate-synthesizer`. (4) Backend failure →
> halt and log to `references/map-debt.md`. No workarounds.

---

## 🎭 Identity: The Sub-Agent Dispatcher

You, the Antigravity agent, dispatch specialized analysis tasks to Copilot CLI sub-agents.

> [!IMPORTANT]
> **Billing model: AI Credits (token-based, effective June 1 2026).** All models consume AI credits at per-token rates — there are no longer "included" or "free" models for chat/agent interactions. Code completions and Next Edit Suggestions remain unlimited for paid plans. Copilot CLI interactive default is `claude-sonnet-4.6`; `run_agent.py` defaults to `gpt-5-mini` for cost efficiency. See [💰 AI Credits & Cost Discipline](#-ai-credits--cost-discipline) and `references/copilot-models.json` for full pricing.

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
# Signature:
python ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" [MODEL] [isolated]
#                                                                                           ^        ^
#                                                                                           optional optional (default: false)
```

### Two dispatch modes

**Task dispatch** (default — agent has full filesystem access via `--yolo`):
```bash
# Agent reads/writes files directly. Pass the task prompt as INPUT_FILE.
python plugins/cli-agents/scripts/run_agent.py \
  /dev/null \
  tasks/todo/copilot_prompt_0025.md \
  temp/copilot_output_0025.md \
  "Implement all changes specified in the prompt." \
  claude-sonnet-4.6
```

**Isolated analysis** (no filesystem tools — text output only):
```bash
# Pass isolated=true as 6th arg. Agent generates text output only.
python plugins/cli-agents/scripts/run_agent.py \
  agents/security-auditor.md target.py security.md \
  "Find vulnerabilities." gpt-5-mini true
```

### Prompt assembly (handled automatically by `run_agent.py`)

| Inputs present | Assembled prompt |
|:---|:---|
| persona + input | `persona / ---SOURCE--- input / ---INSTRUCTION--- instruction` |
| input only (task dispatch) | `input / ---INSTRUCTION--- instruction` |
| instruction only (heartbeat) | `instruction` |

Passing `/dev/null` for persona or input skips that block cleanly.

---

## 🔀 Model Selection Guide

> Full model data (identifiers, per-token costs, context windows): `references/copilot-models.json`

### Default for `run_agent.py`: `gpt-5-mini` (cheapest, best for most tasks)

```bash
# No model arg = gpt-5-mini (25 credits/1M input, 200 credits/1M output)
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Find vulnerabilities."
```

### Value pick for coding tasks: `mai-code-1-flash` (new Jun 2026)

```bash
# Microsoft MAI-Code-1-Flash — Microsoft claims similar quality to claude-sonnet-4.6 at ~4× lower cost
# Input: 75 credits/1M  Output: 450 credits/1M  (vs Sonnet: 300 input / 1500 output)
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Audit for OWASP Top 10 vulnerabilities." mai-code-1-flash
```

### Absolute cheapest: `gpt-5.4-nano`

```bash
# GPT-5.4 nano: 20 credits/1M input, 125 credits/1M output — cheapest in catalog
python ./scripts/run_agent.py /dev/null /dev/null heartbeat.md \
  "HEARTBEAT CHECK: Respond HEARTBEAT_OK only." gpt-5.4-nano
```

### Complex reasoning / multi-file: `claude-sonnet-4.6`

```bash
# 300 credits/1M input, 1500 credits/1M output. Batch everything into one call.
python ./scripts/run_agent.py /dev/null /tmp/copilot_prompt.md /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4.6
```

### Model Identifiers & Credit Costs (June 2026 — AI Credits billing)

> [!NOTE]
> 1 AI Credit = $0.01 USD. All costs are per 1 million tokens. Copilot CLI interactive session default is `claude-sonnet-4.6`; `run_agent.py` defaults to `gpt-5-mini`.

| Model | Identifier | Input cr/1M | Output cr/1M | Notes |
|:---|:---|---:|---:|:---|
| **GPT-5.4 nano** | `gpt-5.4-nano` | 20 | 125 | Cheapest overall |
| **GPT-5 mini** | `gpt-5-mini` | 25 | 200 | Best default — fast, cheap |
| Raptor mini | `raptor-mini` | 25 | 200 | GitHub fine-tuned, same cost as gpt-5-mini |
| Gemini 3 Flash | `gemini-3-flash` | 50 | 300 | Preview |
| **MAI-Code-1-Flash** | `mai-code-1-flash` | 75 | 450 | **New Jun 2026** — code-focused, 256K ctx, no cache write cost |
| GPT-5.4 mini | `gpt-5.4-mini` | 75 | 450 | Same price tier as MAI-Code-1-Flash |
| Claude Haiku 4.5 | `claude-haiku-4.5` | 100 | 500 | Cheapest Anthropic; +125 cr/1M cache write |
| Gemini 2.5 Pro | `gemini-2.5-pro` | 125 | 1000 | Good reasoning at moderate cost |
| Gemini 3.5 Flash | `gemini-3.5-flash` | 150 | 900 | Better via agy CLI |
| GPT-5.3-Codex | `gpt-5.3-codex` | 175 | 1400 | Code-specialist, high output cost |
| Gemini 3.1 Pro | `gemini-3.1-pro` | 200 | 1200 | Preview; long ctx doubles cost above 200K |
| GPT-5.4 | `gpt-5.4` | 250 | 1500 | Long ctx doubles above 272K |
| **Claude Sonnet 4.6** | `claude-sonnet-4.6` | 300 | 1500 | **Copilot default** — best reasoning; +375 cr/1M cache write |
| Claude Sonnet 4.5 | `claude-sonnet-4.5` | 300 | 1500 | Prefer 4.6 (same price, newer) |
| Claude Opus 4.8 | `claude-opus-4.8` | 500 | 2500 | Highest Anthropic quality; +625 cr/1M cache write |
| Claude Opus 4.7 | `claude-opus-4.7` | 500 | 2500 | Same price as Opus 4.8; prefer 4.8 |
| Claude Opus 4.6 | `claude-opus-4.6` | 500 | 2500 | Same price as Opus 4.8 |
| GPT-5.5 | `gpt-5.5` | 500 | 3000 | Very expensive output; avoid unless justified |
| Claude Fable 5 | `claude-fable-5` | 1000 | 5000 | **UNAVAILABLE** — currently withdrawn |

> [!WARNING]
> **Model identifiers use dots not dashes in version numbers** — `claude-sonnet-4.6` not `claude-sonnet-4-6`. Verify current identifiers with `/model` in an interactive session before any expensive run. Deprecated: `gpt-4.1`, `gpt-4o`, `claude-sonnet-4`, `gpt-5.2`/`gpt-5.2-codex`.

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
Always add these instructions to your dispatch prompt to prevent the sub-agent from attempting to use external tools. Default to `gpt-5-mini` for cost efficiency; use `mai-code-1-flash` for code tasks where quality matters.

### 4. 💡 Improve Quality
To dramatically improve review results, add:
> "Think step-by-step internally, but output only final results. Be strict and critical. Do not be polite."

---

## 💰 AI Credits & Cost Discipline

> [!CAUTION]
> **AI Credits billing (effective June 1, 2026): all models consume credits at per-token rates.** 1 Credit = $0.01 USD. Credits do NOT roll over monthly. When credits are exhausted, Copilot stops — no fallback model. Set additional-spend cap to $0 in GitHub billing settings to hard-stop at your allotment.
>
> **Code completions and Next Edit Suggestions are excluded — still unlimited for paid plans.** Annual plan subscribers stay on legacy PRU pricing until their plan expires.

### Monthly Credit Allotments

| Plan | $/month | Credits/month | Notes |
|:---|:---|:---|:---|
| Copilot Pro | $10 | 1,000 | Individual |
| Copilot Pro+ | $39 | 3,900 | Individual |
| Copilot Business | $19/user | 1,900 (pooled) | Business (promotional: 3,000 Jun–Aug 2026) |
| Copilot Enterprise | $39/user | 3,900 (pooled) | Enterprise (promotional: 7,000 Jun–Aug 2026) |

### Model Strategy

| Use case | Model | Reasoning |
|:---|:---|:---|
| Heartbeat / connectivity check | `gpt-5.4-nano` | Cheapest (20 cr/1M in) |
| Default / high-frequency tasks | `gpt-5-mini` | 25 cr/1M — best routine default |
| Code analysis / code review | `mai-code-1-flash` | 75 cr/1M — Microsoft claims Sonnet-level quality for code at 4× lower cost |
| Claude quality, cost-efficient | `claude-haiku-4.5` | 100 cr/1M — best Claude reasoning per credit |
| Complex reasoning / multi-file generation | `claude-sonnet-4.6` | 300 cr/1M — Copilot's default; best for nuanced work |
| Critical / highest-quality tasks only | `claude-opus-4.8` | 500 cr/1M — 5× more than Sonnet; justify before using |
| Avoid | `gpt-5.5` (long ctx), `claude-fable-5` | Extremely expensive; Fable 5 currently unavailable |

### Rules for All Model Calls (not just premium)

1. **Plan before calling; batch for output quality.** Two distinct reasons to minimize requests:
   - **Planning** reduces wasted tokens — a well-specified prompt avoids correction requests that each re-pay full context cost.
   - **Batching** improves coherence — one call generating 7 files produces internally consistent output that 7 separate calls won't.
2. **Use structured output delimiters** so one response parses into multiple files:
   ```
   ===FILE: [relative/path/to/file]===
   [complete file content]
   ===ENDFILE===
   ```
3. **Verify delimiter coverage before calling.** Count expected `===FILE:===` markers in your prompt — confirm the same count appears in output before parsing.
4. **No follow-up requests for minor gaps.** Fill small omissions yourself. Only make a second high-cost request if a whole file is entirely missing.
5. **Heartbeat with `gpt-5.4-nano` or `gpt-5-mini`.** Run connectivity checks against the cheapest model — verifies Copilot CLI is working without spending meaningful credits.
6. **Do NOT background (`&`) expensive model calls.** Large prompts can silently produce empty output in background processes. Run foreground and verify with `wc -l` (expect 200+ lines for multi-file output).

### Premium Model Invocation Pattern

```bash
# Write the full multi-file prompt to a temp file first
cat > /tmp/copilot_prompt.md << 'PROMPT_EOF'
[Your complete, dense, multi-file generation prompt]
PROMPT_EOF

# Dispatch ONE request — all output in a single call
python ./scripts/run_agent.py \
  /dev/null \
  /tmp/copilot_prompt.md \
  /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4.6

# Verify output is substantial before parsing
wc -l /tmp/copilot_output.md   # expect 200+ lines for multi-file output
```

### Quality Gate Before Parsing

```bash
# Confirm all expected FILE markers are present before assuming success
grep -c '===FILE:' /tmp/copilot_output.md  # should equal your expected file count
```

---

## ✅ Functional CLI Heartbeat (Mandatory: "All Signals Go")

Before initiating major orchestrations or long-running iterative loops (e.g., Triple-Loop), you **MUST** perform a zero-shot heartbeat check to verify the host CLI has end-to-end connectivity and correct model defaults.

### Heartbeat Pattern:
```bash
python .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null ./HEARTBEAT_MD.md \
  "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."

# Verification Logic:
[ -s ./HEARTBEAT_MD.md ] && grep -q "HEARTBEAT_OK" ./HEARTBEAT_MD.md && echo "HEARTBEAT_OK" || echo "HEARTBEAT_FAIL"
```

**Logging Requirement**: The result of this heartbeat (Success or Failure) MUST be explicitly written to the session log before proceeding. If it fails, halt execution and report the error details (e.g., `401 Unauthorized`, `429 Rate Limit`, or `Network Error`).

---

## ✅ Smoke Test

```bash
python ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```

Examine `output.md`. It should contain ONLY the refactored code and a brief 3-bullet summary.

---

## Gotchas (field-tested)

- **Model identifiers use dots, not dashes.** `claude-sonnet-4.6` works; `claude-sonnet-4-6` returns "model not available". Always use dot notation for Claude version numbers in Copilot CLI.
- **Always verify the model identifier before a premium batch run.** Run `copilot --yolo --model <id> -p "HEARTBEAT_OK"` first — if it echoes back any response, the identifier is valid. Do not assume identifiers from docs or memory are current.
- **`run_agent.py` passes the 5th argument directly to `--model`.** If the identifier is wrong, the script exits with a non-zero code and produces no output file. Check exit code and output file size before claiming success.
- **Background premium runs can silently fail with empty output.** Never background (`&`) a premium model call. Run foreground and verify with `wc -l output.md` — expect 200+ lines for multi-file output.
- **Heartbeat with `gpt-5-mini`, not a credit-consuming model.** It's an included model — connectivity checks cost nothing.
- **`permissions.disableBypassPermissionsMode` setting** (v1.0.55+) — can lock out `--yolo`/allow-all mode. If headless dispatch stops working, check this setting hasn't been set to `true` by an org admin.
- **Recursive skill/agent discovery** (v1.0.55+) — Copilot CLI now discovers agents and skills in subdirectories, not just the root `.agents/` level. Nested layouts work.
- **Per-MCP-server token usage** now visible in `/mcp` and `/context` — use this to audit which MCP tools are consuming credits.
