# Provider Fallback Routing & Multi-Subscription Pooling

This reference defines the architecture for cross-provider model routing, local proxy failovers, and multi-subscription pooling to prevent quota bottlenecks during autonomous CLI agent loops.

---

## 1. Problem & Architecture

When running intensive multi-agent CLI workflows (`claude`, `codex`, `copilot`, `agy`), developers holding multiple paid plans (Claude Pro, ChatGPT Plus, Gemini Pro, GitHub Copilot) frequently encounter rolling quota limits (e.g., Claude 5-hour message windows, ChatGPT 3-hour caps).

```
                      ┌────────────────────────────────────────┐
                      │    Local Agent CLI Invocations         │
                      │ (run_agent.py / Claude / Codex / Agy)  │
                      └──────────────────┬─────────────────────┘
                                         │
                   Transparent API Redirect (ANTHROPIC_BASE_URL /
                                             OPENAI_BASE_URL)
                                         ▼
                      ┌────────────────────────────────────────┐
                      │   Local Proxy Gateway (:4000 / :8080)  │
                      │ (LiteLLM Proxy / CLIProxyAPI Gateway)  │
                      └───────┬──────────────────────┬─────────┘
                              │                      │
                   Primary Pool Active        429 Rate Limit Detected
                              │                      │
                              ▼                      ▼
                     ┌────────────────┐     ┌────────────────┐
                     │ Primary Quota  │     │ Failover Pool  │
                     │ (e.g. Claude   │     │ (e.g. Copilot  │
                     │  Pro Native)   │     │  Sonnet/Gemini)│
                     └────────────────┘     └────────────────┘
```

---

## 2. Gateway Proxy Options

### Option A: LiteLLM Proxy + Copilot Bridge (Recommended for Standard Teams)
* **Mechanism**: Runs a robust local Python/uvicorn daemon on `localhost:4000`. Translates standard Anthropic (`/v1/messages`) and OpenAI (`/v1/chat/completions`) endpoints.
* **Key Strengths**: True streaming support, zero schema corruption on complex multi-file diffs, and predictable priority fallback defined in a local `config.yaml`.

### Option B: CLIProxyAPI (Recommended for Multi-Subscription Developers)
* **Mechanism**: Intercepts CLI agent requests and pools authenticated credentials from GitHub Copilot, Cursor Pro, Claude Pro, and Gemini CLI.
* **Key Strengths**: Automatically tracks 5-hour rolling windows and dynamically rotates accounts when soft caps approach.

### Prohibited Architecture: 9Router / NymRouter
* **Risk**: Hijacks browser OAuth cookies and redirects to unauthorized free tiers.
* **Failure Modes**: Session cookies expire without warning, provider security blocks accounts, and tool-call translations silently corrupt git diffs. **Never use in production coding pipelines.**

---

## 3. Work vs. Personal Boundary Governance

* **Work / Employer Constraints**:
  * Tools provided through employer or corporate seats (e.g., GitHub Copilot Enterprise) must be isolated to work-related projects.
  * Never route personal, proprietary, or sovereign AI research traffic through corporate-monitored telemetry rails.
* **Sovereign / Personal Subscriptions**:
  * Independent personal subscriptions (ChatGPT Plus, Claude Pro, Gemini Pro) pool together to handle personal coding tasks.
  * Local offline models (`llama-server` running Gemma 4 on port 8089) serve as the ultimate air-gapped zero-cost fallback.

---

## 4. Execution Contract & Environment Variables

When a local proxy is running, CLI agents redirect seamlessly via standard environment variables:

```bash
# Redirect Anthropic traffic to local gateway
export ANTHROPIC_BASE_URL="http://localhost:4000"

# Redirect OpenAI traffic to local gateway
export OPENAI_BASE_URL="http://localhost:4000/v1"
```

In `run_agent.py`, the runner probes `http://localhost:4000/health` or `http://localhost:8080/health`. If healthy and authorized by project policy, the base URLs are injected into the child process environment automatically.
