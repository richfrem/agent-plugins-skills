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
> **Billing model: AI Credits (token-based, effective June 1 2026).** All models consume AI credits at per-token rates — there are no longer "included" or "free" models for chat/agent interactions. Code completions and Next Edit Suggestions remain unlimited for paid plans. The interactive default is account-defined; `run_agent.py` resolves its default from the authoritative cheapest-model reference. See [💰 AI Credits & Cost Discipline](#-ai-credits--cost-discipline) and `references/copilot-models.json` for current IDs and pricing.

## Native orchestration facilities (verified September 2026)

Copilot CLI has native plan mode (`--plan` or `--mode plan`), autopilot for executing an
accepted plan, custom agents, and model-initiated subsidiary agents. Use native delegation only
for independent workstreams; the model may choose to work directly. The CLI can resume a
session from an existing worktree but does **not** document a command to create or manage a Git
worktree. Create the control-plane portable worktree before launching Copilot.

```bash
# Create a plan interactively; keep user approval before autopilot
copilot --plan

# Start with a named custom agent when it is the correct specialist
copilot --agent code-review
```

`--autopilot`, `--allow-all`, and `--yolo` increase autonomy or permissions; none substitutes
for user approval, a bounded scope, or control-plane receipts. Set `--max-ai-credits` for a
paid session where a hard cost ceiling is required.

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

For review dispatches, add `--require-input` when the source is mandatory. Missing or empty
source files fail before the backend command is built. Supplied source is always enclosed in
`---SOURCE---` / `---END SOURCE---`, including persona-free dispatches. Record critic results
through the control-plane `record-critic-review` command using canonical `PASS`, `REVISE`, or
`REJECT`; external `REQUEST_CHANGES` is normalized to `REVISE`, and only `PASS` satisfies the
approval gate.

---

## 🔀 Model Selection Guide

> Full model data (identifiers, per-token costs, context windows): `references/copilot-models.json`

### Model selection

`update-cli-models` is the sole authority for current Copilot model IDs, picker
availability, capability tiers, pricing, and synchronized catalog copies. Read
`references/copilot-models.json` through that authority before selecting a model;
this skill does not duplicate the model catalog. `run_agent.py` resolves its
low-tier default from `references/cheapest_models.json` and accepts an explicit
catalog-backed `--model` or `--tier` override.

```bash
# No model arg = the current low-cost Copilot model from cheapest_models.json
python ./scripts/run_agent.py agents/security-auditor.md target.py security.md \
  "Find vulnerabilities."
```

### Tiered dispatch

```bash
# Resolve the selected tier from the current catalog; inspect the resolved ID
# and account authorization before any paid dispatch.
python ./scripts/run_agent.py /dev/null /tmp/copilot_prompt.md /tmp/copilot_output.md \
  "Generate all files exactly as specified using ===FILE:=== delimiters." \
  --cli copilot --tier high
```

> [!WARNING]
> Copilot model identifiers and display names can differ. Verify the exact identifier with `models.list` or an interactive `/model` command before an expensive run. Static catalog prices are advisory and account authorization still applies.

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
| Heartbeat / connectivity check | Resolve `--tier low` from the catalog | Lowest currently verified tier |
| Default / high-frequency tasks | Resolve `--tier low` from the catalog | Use current catalog pricing |
| Code analysis / code review | Choose from the current catalog | Match quality and budget to the task |
| Claude quality, cost-efficient | `claude-haiku-4-5` | Cheapest current Claude model; verify Copilot ID |
| Complex reasoning / multi-file generation | `claude-opus-5` or `claude-sonnet-5` | Select by required quality and budget |
| Critical / highest-quality tasks only | Choose from the current high tier | Justify before use |
| Avoid | Retired entries in the catalog | Use only models marked available and confirmed by `models.list` |

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
5. **Heartbeat with the catalog-resolved low tier.** Run connectivity checks against the cheapest current model without hardcoding a stale identifier.
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
