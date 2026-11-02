# Multi-Subscription Cloud Routing & Gateway Setup (M1 Apple Silicon)

## 1. Context & Hardware Grounding (Apple Silicon M1)

Running resource-heavy local LLMs (e.g. 70B models or slow local 7B servers) inside background agent loops on an **Apple Silicon M1 Mac** creates severe operational friction: high RAM pressure, thermal throttling, battery drain, and sluggish response times.

Developers maintaining multiple paid commercial subscriptions do not need local LLM compute. Instead, the optimal strategy is **Cloud-to-Cloud Multi-Subscription Pooling**: seamlessly rotating across paid cloud endpoints when individual rolling rate windows or message quotas approach.

---

## 2. Personal Subscription Inventory & Separation Invariant

| Subscription Tier | CLI Binary | Native Strengths | Quota Window | Pool Status |
|---|---|---|---|---|
| **Claude Pro ($20/mo)** | `claude` (Claude Code) | Architectural planning, deep reasoning | ~45 msgs / 5 hours | **Primary Tier 1** |
| **Gemini Pro (Google One)** | `agy` (Antigravity) | 2M ultra-long context, multimodal vision | 1,500 requests / day | **Failover Tier 2** |
| **ChatGPT Plus ($20/mo)** | `codex` (Codex CLI) | Fast procedural coding, Luna 6.0 / Sol 6.1 | ~40-80 msgs / 3 hours | **Failover Tier 3** |
| **Cursor Premium ($30/mo)** | `cursor-agent` / Grok Bot | Infinite cloud VM loops, email/telephony | 4x Plus usage pool | **Asynchronous VM** |
| **GitHub Copilot (Enterprise)**| `copilot` | Copilot workspace CLI | Enterprise seats | **STRICTLY WORK ONLY** |

> [!IMPORTANT]
> **Supreme Law Governance Invariant**:
> GitHub Copilot is provisioned for enterprise and work-related repositories only. **It must NEVER be pooled or routed for personal or sovereign research.**

---

## 3. Subscription Routing Architectures

```
                         ┌────────────────────────────────────────┐
                         │      Local Agent CLI Dispatch          │
                         │ (run_agent.py / Claude / Codex / Agy)  │
                         └──────────────────┬─────────────────────┘
                                            │
                                            ▼
                         ┌────────────────────────────────────────┐
                         │   Pre-Flight Readiness Check           │
                         │   (check_routing_readiness.py)         │
                         └──────────────────┬─────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
     ┌─────────────────────────────┐                 ┌─────────────────────────────┐
     │ Strategy A: Local Proxy     │                 │ Strategy B: Native CLI      │
     │ Gateway (Port 4000)         │                 │ Fallback Chain              │
     ├─────────────────────────────┤                 ├─────────────────────────────┤
     │ • Transparent intercept     │                 │ • Zero daemon overhead      │
     │ • ANTHROPIC_BASE_URL redirect│                │ • Direct CLI tool calls     │
     │ • Automatic 429 failover    │                 │ • Automatic --fallback-chain│
     └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
      ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
      │  Claude Pro     │ ──(429)─►│  Gemini Pro     │ ──(429)─►│  ChatGPT Plus   │
      │  (Primary Tier) │          │  (Failover 1)   │          │  (Failover 2)   │
      └─────────────────┘          └─────────────────┘          └─────────────────┘
```

### Strategy A: Transparent Proxy Gateway (:4000)
A local lightweight gateway listening on `localhost:4000` intercepts standard Anthropic (`/v1/messages`) and OpenAI (`/v1/chat/completions`) requests:
* **Activation**:
  ```bash
  export ANTHROPIC_BASE_URL="http://localhost:4000"
  export OPENAI_BASE_URL="http://localhost:4000/v1"
  ```
* **Behavior**:
  - Forwards primary requests to Anthropic Claude Pro using the user's authentic credentials.
  - If a `429 Too Many Requests` or rate-limit response is received, the proxy automatically translates the payload to Gemini Pro or Codex without aborting the task.

### Strategy B: Native Multi-CLI Fallback Chain (Zero Daemon)
For CLI-level task dispatching in `run_agent.py`, invoke with a declared fallback chain:
```bash
python scripts/run_agent.py <PERSONA> <INPUT> <OUTPUT> "<TASK>" \
    --cli claude --fallback-chain agy,codex
```
If `claude` exits with a rate limit or failure, `run_agent.py` automatically retries the identical prompt through `agy` (Gemini Pro), then `codex` (ChatGPT Plus).

---

## 4. Pre-Flight Readiness Validation

Before initiating long-running or token-intensive tasks, execute the pre-flight readiness probe:

```bash
python3 scripts/check_routing_readiness.py
```

### Sample Output:
```
=================================================================
      MULTI-SUBSCRIPTION ROUTING & GATEWAY READINESS PROBE       
=================================================================
Hardware Optimization : Apple Silicon (M1/M2/M3) Optimized - Local LLMs Bypassed
Overall Posture       : [LOCAL_PROXY_ACTIVE]
Readiness Summary     : Local proxy gateway active on port 4000. Traffic transparently intercepted.
-----------------------------------------------------------------
1. Gateway Daemon Status:
   Port 4000          : [ACTIVE] (HTTP 200 on /v1/models (port 4000))
   ANTHROPIC_BASE_URL : http://localhost:4000
   OPENAI_BASE_URL    : http://localhost:4000/v1
-----------------------------------------------------------------
2. Cloud Subscriptions Available (Personal):
   • claude   [INSTALLED] - Claude Pro ($20/mo) -> /Users/.../.local/bin/claude
   • agy      [INSTALLED] - Gemini Pro / Google One -> /opt/homebrew/bin/agy
   • codex    [INSTALLED] - ChatGPT Plus ($20/mo) -> /opt/homebrew/bin/codex
-----------------------------------------------------------------
3. Corporate Boundary Governance:
   • copilot  : INSTALLED (Strictly Work Only)
     (Must NEVER be routed to personal or sovereign research)
=================================================================
```

---

## 5. Troubleshooting & Health Recovery

1. **Gateway Port 4000 Not Responding**:
   - Check if the daemon is loaded: `launchctl list | grep local-llm-proxy`
   - Start the service: `python3 scripts/enable_global_routing.py`
2. **Rate Limit 429 on Claude Pro**:
   - Verify that fallback to `agy` or `codex` is active.
   - Do NOT spin up local `llama-server` on M1; dispatch to `agy --model gemini-3.8-flash` or `codex -m gpt-6-luna` instead.
3. **Copilot Leak Prevention**:
   - Audit `context/user.md` and environment variables. If `GITHUB_TOKEN` or `COPILOT_API_KEY` is present in personal sessions, unset it: `unset COPILOT_API_KEY`.
