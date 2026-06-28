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

## 🎭 Identity: The Sub-Agent Dispatcher (Standard: gpt-5-mini)

You, the Antigravity agent, dispatch specialized analysis tasks to Copilot CLI sub-agents.

> [!IMPORTANT]
> **Default model: `gpt-5-mini` (included — no credit cost).** As of June 1, 2026, GitHub moves to **AI Credits** (per-token billing), but `gpt-5-mini` is an included model that does not consume credits. Higher-multiplier models (e.g., `claude-sonnet-4.6`) do consume credits — see [💰 AI Credits & Cost Discipline](#-ai-credits--cost-discipline) before using them.

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

### Default: `gpt-5-mini` (included — no credit cost)

```bash
# No model arg = gpt-5-mini (included model, does not consume credits)
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Find vulnerabilities."
```

### High-quality: `claude-sonnet-4.6` (9x multiplier — batch everything)

```bash
# Pass model name as the 5th argument to override the default
python ./scripts/run_agent.py /dev/null /tmp/copilot_prompt.md /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4.6
```

> [!NOTE]
> **When to use `claude-sonnet-4.6`:** Complex multi-file generation, nuanced content requiring reasoning, tasks where output quality matters more than cost. See [💰 AI Credits & Cost Discipline](#-ai-credits--cost-discipline) for batching rules before calling.

### Known Model Identifiers (June 2026)

| Model | Identifier | Credit cost |
|:---|:---|:---|
| GPT-5 mini | `gpt-5-mini` | Included (no credits) |
| GPT-4.1 | `gpt-4.1` | Included (deprecation upcoming) |
| GPT-4o | `gpt-4o` | Included |
| Claude Haiku 4.5 | `claude-haiku-4.5` | Low |
| GPT-5.4 | `gpt-5.4` | 6x |
| GPT-5.4 mini | `gpt-5.4-mini` | 6x |
| Claude Sonnet 4.5 | `claude-sonnet-4.5` | 9x |
| Claude Sonnet 4.6 | `claude-sonnet-4.6` | 9x |
| Gemini 3.5 Flash | `gemini-3.5-flash` | (verify current) |
| Claude Opus 4.7 | `claude-opus-4.7` | 27x |
| Claude Opus 4.8 | `claude-opus-4.8` | 27x |

> [!WARNING]
> **Model identifiers use dots not dashes** — `claude-sonnet-4.6` not `claude-sonnet-4-6`. Identifiers change with Copilot CLI updates — run `copilot -i "list models"` or check the interactive model selector to confirm current names before any high-multiplier run.
>
> **Deprecated (do not use):** `claude-sonnet-4` (deprecated May 7), `gpt-5.2` / `gpt-5.2-codex` (deprecated). GPT-4.1 deprecation upcoming.

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

## 💰 AI Credits & Cost Discipline

> [!CAUTION]
> **As of June 1, 2026, GitHub Copilot moves to AI Credits (per-token billing).** 1 Credit = $0.01. Credits do NOT roll over monthly. When credits are exhausted, Copilot stops — there is no fallback model. Set your additional-spend cap to $0 in GitHub billing settings to hard-stop at your monthly allotment.
>
> **`gpt-5-mini`, `gpt-4.1`, and `gpt-4o` remain included models (no credit cost).** Annual plan subscribers stay on PRU-based pricing until their plan expires, then roll to the new Credit model. Code completions and Next Edit Suggestions never consume credits.

### Credit Cost by Tier

| Tier | Credits/month | Overage |
|:---|:---|:---|
| Copilot Pro ($10/mo) | 1,000 | Optional, per credit |
| Copilot Pro+ ($39/mo) | 3,900 | Optional, per credit |
| Business ($19/user/mo) | $19 worth (pooled) | Optional |

### Strategy by Cost Tier

| Model | Cost | Use when |
|:---|:---|:---|
| `gpt-5-mini`, `gpt-4.1`, `gpt-4o` | Included | Default — always prefer |
| `claude-haiku-4.5` | Low credits | When Claude quality needed cheaply |
| `gpt-5.4`, `gpt-5.4-mini` | Moderate credits | Moderate quality step-up |
| `claude-sonnet-4.6` | High credits | Complex reasoning, multi-file generation |
| `claude-opus-4.7`, `claude-opus-4.8` | Highest credits | Critical tasks only |

### Rules for Credit-Consuming Models

1. **Plan before calling; batch for output quality.** Two distinct reasons to minimize requests:
   - **Planning** reduces wasted tokens — a well-specified prompt avoids correction requests, which each re-pay the full context cost. Think through requirements before dispatching.
   - **Batching** improves coherence and reduces round-trips — a single call generating 7 files produces internally consistent output that 7 separate calls won't. Under AI Credits the total token cost is the same either way, but the quality and latency are better batched.
2. **Use structured output delimiters** so one response parses into multiple files:
   ```
   ===FILE: [relative/path/to/file]===
   [complete file content]
   ===ENDFILE===
   ```
3. **Verify delimiter coverage before calling.** Count expected `===FILE:===` markers in your prompt — confirm the same count appears in output before parsing.
4. **No follow-up requests for minor gaps.** Fill small omissions yourself. Only make a second high-multiplier request if a whole file is entirely missing.
5. **Heartbeat with `gpt-5-mini`.** Run the heartbeat against the cheapest model only — it verifies connectivity without burning credits.
6. **Do NOT background (`&`) high-multiplier calls.** Large prompts can silently produce empty output in background processes. Run foreground and verify with `wc -l` (expect 200+ lines for multi-file output).

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
