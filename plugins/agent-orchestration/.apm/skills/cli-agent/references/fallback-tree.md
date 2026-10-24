# Procedural Fallback Tree: CLI Agent

Unified procedural fallback rules for all CLI agent backends (Claude, Copilot, Codex, Antigravity, and Local Llama).

## Core Invariant

**One backend per task: halt, log to `map-debt.md`, and surface to the caller. Zero silent fallback to alternate backends or simulated inline behavior.**

## Fallback Decision Matrix

| Failure Condition | Affected Backends | Required Action & Remediation |
| :--- | :--- | :--- |
| **CLI Not Found on PATH** | All | Report the missing executable and the official install command:<br>• Claude: `npm i -g @anthropic-ai/claude-code`<br>• Copilot: Standalone `@github/copilot` or official CLI<br>• Codex: OpenAI Codex binary install<br>• Antigravity: `gemini` / `agy` package install<br>• Local LLM: Start via `python3 scripts/run_server.py`<br>Use `--executable <path>` for non-standard paths. Do **NOT** simulate CLI responses inline. |
| **Version Probe Unsupported** | All | Report the backend as unavailable. Do **NOT** pick an alternate binary without explicit authorization. |
| **Smoke / Heartbeat Failure** | Copilot, Llama | **HALT** before dispatching the full analysis task.<br>• Copilot: verify `COPILOT_CLI_OK` response.<br>• Llama: verify `curl http://localhost:8089/health`.<br>Model calls during heartbeat must be authorized. Report failure and prompt user to re-authenticate or restart. |
| **Hangs Waiting for UI Approval** | Claude Code | Terminate the hanging process immediately. Under `--isolated`, `--dangerously-skip-permissions` is suppressed by design (Rule 3). Do **NOT** auto-retry with elevated permissions. Ask for user authorization or re-dispatch with proper input file bindings. |
| **Elevated Permissions Requested** | Claude, Copilot | Flags such as `--dangerously-skip-permissions`, `--allow-all-tools`, `--allow-all-paths`, or `--yolo` require explicit user confirmation. Document the operational reason in the command invocation. |
| **Input Too Large (~5MB Pipe Limit)** | All | Split the input semantically using a Python chunking script before dispatching. Run separate chunk analysis passes. Do **NOT** attempt to force large payloads through a single pipe or CLI argument. Note: `run_agent.py` uses prompt file / stdin redirection rather than argv. |
| **Authentication Failure** | All | Surface the exact authentication error. The human operator must authenticate interactively:<br>• Claude: `claude login`<br>• Copilot: interactive authentication flow<br>• Codex: `codex login`<br>• Antigravity: `gemini auth`<br>Never retry authentication in a background worker. Never log tokens or credentials. |
| **Quota / Rate Limit / Timeout** | All | For timeouts (e.g. Agy `--print-timeout`) or API rate limits, **HALT** immediately. Do **NOT** switch to another backend or cycle model requests in a retry loop. Surface error to caller. |
| **Empty or Below-Threshold Output** | All | Empty, truncated, or failed output is **NOT** a completed review. **HALT** → log a Tier 0 entry in `references/map-debt.md` → surface failure to caller (Execution Contract Rule 4). |
| **Local Llama Server Down / Port Busy** | Llama | Probe `http://localhost:8089/health`. If unreachable or port is busy, launch `python3 scripts/run_server.py`. Verify `kv_cache` slot allocation. Do **NOT** silently fall back to cloud backends. |
| **Profile Invalid or Stale** | All | If `context/agent-capability-profile.json` is missing or stale, fall back to bundled catalog defaults. Never declare an unverified provider available (Execution Contract Rule 5). |
