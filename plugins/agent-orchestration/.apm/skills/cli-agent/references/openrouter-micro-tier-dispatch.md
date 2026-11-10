# OpenRouter Micro-Tier Dispatch

Dispatches bounded mechanical tasks, linting, formatting, and routine triage to ultra-low-cost cloud micro-models (0.5B–3B parameters) via the OpenRouter API. 

This tier acts as a **"Token Shield"** to preserve expensive frontier subscription quotas (Claude Pro, ChatGPT Plus, Gemini Pro) and prevents local edge hardware (Mac disk space and unified RAM) from being consumed by multiple local models.

## Constraints & Requirements

- **Live Data Grounding**: **CRITICAL**: Never rely on static training data or cut-off assumptions for OpenRouter model selection or pricing. Model availability and rates shift dynamically. Always query the live endpoint `https://openrouter.ai/api/v1/models` (or `openrouter-models.json`) to verify active availability and per-token rates.
- **API Key**: Requires `OPENROUTER_API_KEY` exported in environment (`~/.zshrc` or `.env`).
- **Hard Cost Cap**: Enforce monthly hard limit ($10.00) configured at the OpenRouter key level and client-side ledger.
- **Allowed Micro-Models**: Strictly restricted to low-cost micro-models and non-LLM encoders. Full-sized general LLMs (e.g., 70B+, frontier models) are barred from this endpoint.
- **Sub-Agent Isolation**: Bounded tasks wrapped with prompt isolation instructions.

## Verified Micro-Models & Live Pricing (Probed 2026-11-10)

| Model Slug | Parameters | Pricing (per 1M tokens) | Ideal Use Case |
|---|---|---|---|
| `meta-llama/llama-3.2-1b-instruct` | 1 Billion | **$0.027** input / **$0.201** output | Ultra-cheap mechanical formatting, JSON cleanup, regex, and short classification |
| `meta-llama/llama-3.1-8b-instruct` | 8 Billion | **$0.020** input / **$0.040** output | General reasoning & triage (output is **5× cheaper** than 1B at $0.04/M) |
| `qwen/qwen3-coder-30b-a3b-instruct` | 30B (3B active MoE) | **$0.150** input / **$0.600** output | High-capability MoE coding specialist (**40% cheaper output** than flash) |
| `qwen/qwen3-coder-next` | Dense Coder | **$0.120** input / **$0.800** output | Fast dense coding chores and syntax repair |
| `qwen/qwen3.7-flash` | Long-Context | **$0.030** input / **$0.130** output | Massive 1M-token context ingestion for large diffs and logs |
| `cohere/north-mini-code:free` | Free Coder | **$0.000** input / **$0.000** output | Dedicated zero-cost code editing fallback (256k context) |

## Dispatch Syntax (HTTP API)

```bash
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
    -d '{
    "model": "meta-llama/llama-3.2-1b-instruct",
    "messages": [{"role": "user", "content": "Format this JSON payload cleanly."}],
    "max_tokens": 100
  }'
```

## Client Script (`scripts/openrouter_client.py`)

Use the bundled client instead of hand-written HTTP calls. It enforces the constraints above:

- **Hard cap**: refuses to spend past `OPENROUTER_MONTHLY_CAP_USD` (default `10.00`) using a local ledger (`OPENROUTER_SPEND_LEDGER`, default `~/.agent/coordination/openrouter_spend.json`). Check with `--spend`.
- **No black-box routers**: `openrouter/free` and `openrouter/auto` raise `ValueError`; pin a model or take it from `jev_router.py --format cli-flags`.
- **Local fallback**: missing key, cap reached, or request failure diverts to the local OpenAI-compatible server (`LOCAL_LLM_URL`, default `http://127.0.0.1:8080/v1/chat/completions`) at zero cost; pass `--no-local-fallback` to fail instead.
- **Live pricing**: per-call cost is computed from `openrouter-models.json`; unknown models are billed at a conservative fallback rate, never free.

```bash
python3 scripts/openrouter_client.py --model meta-llama/llama-3.2-3b-instruct --format json "Sort these JSON keys alphabetically: {...}"
python3 scripts/openrouter_client.py --spend
```

```python
import sys; sys.path.insert(0, "<cli-agent>/scripts")
from openrouter_client import invoke_micro_tier
res = invoke_micro_tier("Add a trailing comma to this JSON ...", model="meta-llama/llama-3.2-3b-instruct", max_tokens=200)
print(res.status, res.cost_usd, res.content)
```

Tests: `pytest scripts/test_openrouter_client.py` (no network; fallbacks are mocked).

### End-to-End Smoke Test (live, ~$0.00001)

```bash
python3 scripts/smoke_test_openrouter.py            # uses references/openrouter-smoke-task.json
python3 scripts/smoke_test_openrouter.py --task my_task.json
```

Routes one test-matrix-shaped task through `jev_router.py`, calls the pinned cheap model through the client with local fallback disabled, and checks four things: routing matches the spec, the live call returned OK without fallback, the output equals `expected_output`, and the spend ledger incremented. Skips cleanly when no `OPENROUTER_API_KEY` is available.

## Verification & Smoke Test

```bash
# Verify 1B micro-tier connectivity
python3 -c "
import os, urllib.request, json
req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {os.environ.get(\"OPENROUTER_API_KEY\")}', 'Content-Type': 'application/json'},
    data=json.dumps({'model': 'meta-llama/llama-3.2-1b-instruct', 'messages': [{'role': 'user', 'content': 'Ping'}], 'max_tokens': 10}).encode('utf-8')
)
with urllib.request.urlopen(req) as resp:
    print('OpenRouter Micro-Tier OK:', json.loads(resp.read().decode('utf-8'))['choices'][0]['message']['content'].strip())
"
```
