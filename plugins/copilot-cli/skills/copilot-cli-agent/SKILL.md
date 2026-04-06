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
> **Default model: `gpt-5-mini` (free tier — no per-request cost).** Use this unless the user explicitly requests a premium model. Premium models (e.g., `claude-sonnet-4-6`) are **charged per request**, not per token — see the [💰 Premium Model Cost Discipline](#-premium-model-cost-discipline) section before using them.

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
python3 ./scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" [MODEL]
#                                                                                           ^ optional 5th arg
```

---

## 🔀 Model Selection Guide

### Default: `gpt-5-mini` (Free — use for most tasks)

```bash
# No model arg = gpt-5-mini (free tier, no per-request cost)
python3 ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Find vulnerabilities."
```

### Premium: `claude-sonnet-4-6` (Charged per request — batch everything)

```bash
# Pass model name as the 5th argument to override the default
python3 ./scripts/run_agent.py /dev/null /tmp/copilot_prompt.md /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4-6
```

> [!NOTE]
> **When to use `claude-sonnet-4-6`:** Complex multi-file generation, nuanced content requiring reasoning, tasks where output quality matters more than cost. See [💰 Premium Model Cost Discipline](#-premium-model-cost-discipline) for request-batching rules before calling.

### Known Model Identifiers

| Model | Identifier | Cost |
|:---|:---|:---|
| GitHub Copilot default | `gpt-5-mini` | Free / flat rate |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Per request (premium) |
| Claude Opus | `claude-opus-4-5` | Per request (premium, highest quality) |

> [!WARNING]
> Model identifiers can change with Copilot CLI updates. If a premium model call fails with a model-not-found error, check `copilot --help` or the [GitHub Copilot model docs](https://docs.github.com/en/copilot/using-github-copilot/ai-models) for the current identifier.

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

## 💰 Premium Model Cost Discipline

> [!CAUTION]
> **Premium models (e.g., `claude-sonnet-4-6`, `claude-opus`) are billed per REQUEST, not per token.** A 5-request workflow costs 5× more than a 1-request workflow with the same total content. **Maximize token density per call — do NOT make iterative follow-up requests.**

### Two-Tier Strategy

| Model | Cost Model | Request Strategy |
|:---|:---|:---|
| `gpt-5-mini` (default) | Free / flat rate | Iterative fine-grained requests are fine |
| `claude-sonnet-4-6`, `claude-opus`, etc. | **Per request** | ONE big dense request — batch everything |

### Rules for Premium Models

1. **ONE request generates ALL output.** If you need 7 files generated, put all 7 specs in a single prompt. Never send 7 separate requests.
2. **Use structured output delimiters** so the single response can be parsed into multiple files:
   ```
   ===FILE: [relative/path/to/file]===
   [complete file content]
   ===ENDFILE===
   ```
3. **Verify delimiter coverage before calling.** Count expected `===FILE:===` markers in your prompt — confirm the same count appears in output before parsing.
4. **No follow-up requests for minor gaps.** If the response has small omissions (a missing line, a thin section), fill them yourself using your own tools. Only make a second premium request if a whole file is entirely missing.
5. **Heartbeat with the free model.** Always run the heartbeat check against `gpt-5-mini` (default), never against a premium model — it's a waste of a paid request.
6. **Do NOT background (`&`) premium model calls.** Large prompt expansions can silently fail in background processes. Run sequentially and verify output with `wc -l` (expect 200+ lines for multi-file generation).

### Premium Model Invocation Pattern

```bash
# Write the full multi-file prompt to a temp file first
cat > /tmp/copilot_prompt.md << 'PROMPT_EOF'
[Your complete, dense, multi-file generation prompt]
PROMPT_EOF

# Dispatch ONE request — all output in a single call
python3 ./scripts/run_agent.py \
  /dev/null \
  /tmp/copilot_prompt.md \
  /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  claude-sonnet-4-6

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
python3 .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null ./HEARTBEAT_MD.md \
  "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."

# Verification Logic:
[ -s ./HEARTBEAT_MD.md ] && grep -q "HEARTBEAT_OK" ./HEARTBEAT_MD.md && echo "HEARTBEAT_OK" || echo "HEARTBEAT_FAIL"
```

**Logging Requirement**: The result of this heartbeat (Success or Failure) MUST be explicitly written to the session log before proceeding. If it fails, halt execution and report the error details (e.g., `401 Unauthorized`, `429 Rate Limit`, or `Network Error`).

---

## ✅ Smoke Test

```bash
python3 ./scripts/run_agent.py agents/refactor-expert.md target.py output.md "Refactor this code."
```

Examine `output.md`. It should contain ONLY the refactored code and a brief 3-bullet summary.
