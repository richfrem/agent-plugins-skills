# OpenRouter Micro-Tier Dispatch

Dispatches bounded mechanical tasks, linting, formatting, and routine triage to ultra-low-cost cloud micro-models (0.5B–3B parameters) via the OpenRouter API. 

This tier acts as a **"Token Shield"** to preserve expensive frontier subscription quotas (Claude Pro, ChatGPT Plus, Gemini Pro) and prevents local edge hardware (Mac disk space and unified RAM) from being consumed by multiple local models.

## Constraints & Requirements

- **API Key**: Requires `OPENROUTER_API_KEY` exported in environment (`~/.zshrc` or `.env`).
- **Hard Cost Cap**: Enforce monthly hard limit ($10.00) configured at the OpenRouter key level and client-side ledger.
- **Allowed Micro-Models**: Strictly restricted to low-cost micro-models and non-LLM encoders. Full-sized general LLMs (e.g., 70B+, frontier models) are barred from this endpoint.
- **Sub-Agent Isolation**: Bounded tasks wrapped with prompt isolation instructions.

## Verified Micro-Models & Pricing

| Model Slug | Parameters | Pricing (per 1M tokens) | Ideal Use Case |
|---|---|---|---|
| `meta-llama/llama-3.2-1b-instruct` | 1 Billion | **$0.027** input / **$0.20** output | Mechanical JSON formatting, regex, basic triage, lint fixes |
| `meta-llama/llama-3.2-3b-instruct` | 3 Billion | **$0.05** input / **$0.33** output | Unit test boilerplate, docstring checks, small script edits |
| `qwen/qwen3-coder-flash` | Micro-Coder | **$0.195** input / **$0.975** output | Fast coding chores, AST-level refactors, syntax repairs |

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
