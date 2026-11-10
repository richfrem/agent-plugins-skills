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
  -H "HTTP-Referer: https://project-sanctuary.local" \
  -H "X-Title: Project Sanctuary" \
  -d '{
    "model": "meta-llama/llama-3.2-1b-instruct",
    "messages": [{"role": "user", "content": "Format this JSON payload cleanly."}],
    "max_tokens": 100
  }'
```

## Python Integration Pattern

```python
import os, urllib.request, json

def query_openrouter_micro(prompt: str, model: str = "meta-llama/llama-3.2-1b-instruct", max_tokens: int = 150) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://project-sanctuary.local",
        "X-Title": "Project Sanctuary",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
```

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
