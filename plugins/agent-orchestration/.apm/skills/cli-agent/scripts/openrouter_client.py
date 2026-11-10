#!/usr/bin/env python3
"""openrouter_client.py - OpenRouter micro-tier client with budget controls.

Backend behind the cli-agent `openrouter` runtime row. Invokes a pinned
low-cost OpenRouter model (0.5B-3B dense, or small-active MoE) for bounded
mechanical tasks while protecting the caller's budget:

- Hard monthly spending cap (default $10.00, override with
  OPENROUTER_MONTHLY_CAP_USD) tracked in a local JSON spend ledger
  (default ~/.agent/coordination/openrouter_spend.json, override with
  OPENROUTER_SPEND_LEDGER).
- Rejection of black-box auto-routers (openrouter/free, openrouter/auto):
  model choice belongs to the caller or to the in-process jev_router.py.
- Automatic fallback to a local OpenAI-compatible server (default
  http://127.0.0.1:8080/v1/chat/completions, override with LOCAL_LLM_URL)
  when the key is missing, the cap is reached, or the request fails.
- Per-call cost computed from references/openrouter-models.json, the
  live-audited catalog. Pricing must come from the live endpoint
  https://openrouter.ai/api/v1/models, never from training-data memory;
  refresh the catalog when rates drift (see model-catalog-maintenance.md).

Key Input Dependencies:
    references/openrouter-models.json  (pricing catalog; optional, falls back
                                        to a conservative default rate)
    OPENROUTER_API_KEY                 (environment; ~/.zshrc is also scanned)

Function Index:
    get_api_key            - resolve the API key from env or ~/.zshrc
    load_pricing_catalog   - read per-1M-token rates from the live-audited catalog
    calculate_cost         - USD cost for a (model, prompt_tokens, completion_tokens)
    get_cumulative_spend   - read the spend ledger
    record_spend           - add a cost to the spend ledger
    call_local_llm         - fallback request to the local OpenAI-compatible server
    invoke_micro_tier      - guarded OpenRouter request with fallback
    main                   - CLI entry point
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(SCRIPT_DIR, "..", "references", "openrouter-models.json")

DEFAULT_MONTHLY_HARD_CAP_USD = 10.00
DEFAULT_SPEND_LEDGER_PATH = os.path.expanduser("~/.agent/coordination/openrouter_spend.json")
DEFAULT_LOCAL_LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-3.2-1b-instruct"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
PROHIBITED_MODEL_PREFIXES = ("openrouter/free", "openrouter/auto")

# Conservative rate used when a model is missing from the catalog, so an
# unknown model is never billed as free.
FALLBACK_RATE: Dict[str, float] = {"prompt": 0.050, "completion": 0.200}


def monthly_hard_cap_usd() -> float:
    """Return the monthly cap, honouring OPENROUTER_MONTHLY_CAP_USD."""
    raw = os.getenv("OPENROUTER_MONTHLY_CAP_USD")
    try:
        return float(raw) if raw else DEFAULT_MONTHLY_HARD_CAP_USD
    except ValueError:
        return DEFAULT_MONTHLY_HARD_CAP_USD


def spend_ledger_path() -> str:
    """Return the spend ledger path, honouring OPENROUTER_SPEND_LEDGER."""
    return os.path.expanduser(os.getenv("OPENROUTER_SPEND_LEDGER") or DEFAULT_SPEND_LEDGER_PATH)


def local_llm_url() -> str:
    """Return the local fallback endpoint, honouring LOCAL_LLM_URL."""
    return os.getenv("LOCAL_LLM_URL") or DEFAULT_LOCAL_LLM_URL


@dataclass
class MicroTierResponse:
    """Standardized response from a micro-tier invocation."""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_s: float
    fallback_triggered: bool
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_api_key() -> Optional[str]:
    """Retrieve OPENROUTER_API_KEY from the environment or ~/.zshrc."""
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key
    zshrc = os.path.expanduser("~/.zshrc")
    if os.path.exists(zshrc):
        with open(zshrc, "r", encoding="utf-8") as f:
            for line in f:
                if "OPENROUTER_API_KEY=" in line and not line.strip().startswith("#"):
                    return line.split("=", 1)[1].strip().strip("\"'")
    return None


def load_pricing_catalog(path: str = CATALOG_PATH) -> Dict[str, Dict[str, float]]:
    """Read per-1M-token rates from the live-audited openrouter-models.json.

    Returns {cli_id: {"prompt": usd, "completion": usd}}. An unreadable catalog
    yields an empty mapping, so every model falls back to FALLBACK_RATE.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    catalog: Dict[str, Dict[str, float]] = {}
    for entry in data.get("models", []):
        cli_id = entry.get("cli_id")
        rates = entry.get("pricing_usd_per_1m") or {}
        if cli_id and "input" in rates and "output" in rates:
            catalog[cli_id] = {"prompt": float(rates["input"]), "completion": float(rates["output"])}
    return catalog


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int,
                   catalog: Optional[Dict[str, Dict[str, float]]] = None) -> float:
    """Compute the USD cost of one call from catalog rates (per 1M tokens)."""
    rates = (catalog if catalog is not None else load_pricing_catalog()).get(model, FALLBACK_RATE)
    return (prompt_tokens / 1_000_000.0) * rates["prompt"] + (completion_tokens / 1_000_000.0) * rates["completion"]


def get_cumulative_spend() -> float:
    """Read the cumulative spend from the ledger (0.0 when absent or unreadable)."""
    path = spend_ledger_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return float(json.load(f).get("cumulative_spend_usd", 0.0))
        except (OSError, ValueError, TypeError):
            return 0.0
    return 0.0


def record_spend(cost_usd: float) -> float:
    """Add a cost to the ledger and return the new cumulative spend."""
    path = spend_ledger_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    updated = get_cumulative_spend() + cost_usd
    data = {
        "cumulative_spend_usd": round(updated, 6),
        "hard_cap_usd": monthly_hard_cap_usd(),
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        sys.stderr.write(f"[openrouter_client] Warning: failed to persist spend: {e}\n")
    return updated


def call_local_llm(prompt: str, max_tokens: int = 512) -> MicroTierResponse:
    """Fallback request to the local OpenAI-compatible server (zero cost)."""
    t0 = time.perf_counter()
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }
    req = urllib.request.Request(
        local_llm_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            content = res_json["choices"][0]["message"]["content"]
            usage = res_json.get("usage", {})
            return MicroTierResponse(
                content=content,
                model="local-server",
                prompt_tokens=usage.get("prompt_tokens", len(prompt) // 4),
                completion_tokens=usage.get("completion_tokens", len(content) // 4),
                cost_usd=0.0,
                latency_s=round(time.perf_counter() - t0, 3),
                fallback_triggered=True,
                status="OK_LOCAL",
            )
    except Exception as e:  # network, HTTP, or malformed body
        return MicroTierResponse(
            content=f"[Local fallback failed: {e}]",
            model="local-server/offline",
            prompt_tokens=0,
            completion_tokens=0,
            cost_usd=0.0,
            latency_s=round(time.perf_counter() - t0, 3),
            fallback_triggered=True,
            status=f"FAILED: {e}",
        )


def invoke_micro_tier(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 512,
    temperature: float = 0.1,
    system_prompt: Optional[str] = None,
    allow_local_fallback: bool = True,
) -> MicroTierResponse:
    """Invoke a pinned OpenRouter micro-model under the hard cap, with local failover.

    Raises ValueError for prohibited auto-router models and RuntimeError when the
    call cannot proceed and local fallback is disabled.
    """
    if any(model.startswith(p) for p in PROHIBITED_MODEL_PREFIXES):
        raise ValueError(
            f"Prohibited model '{model}'. Black-box auto-routers are barred; "
            "pin a model explicitly or route with jev_router.py."
        )

    cap = monthly_hard_cap_usd()
    current_spend = get_cumulative_spend()
    if current_spend >= cap:
        sys.stderr.write(
            f"[openrouter_client] Monthly hard cap ${cap:.2f} reached (${current_spend:.4f}). "
            "Diverting to local server.\n"
        )
        if allow_local_fallback:
            return call_local_llm(prompt, max_tokens=max_tokens)
        raise RuntimeError("Monthly OpenRouter budget exceeded and local fallback disabled.")

    api_key = get_api_key()
    if not api_key:
        sys.stderr.write("[openrouter_client] No OPENROUTER_API_KEY found. Diverting to local server.\n")
        if allow_local_fallback:
            return call_local_llm(prompt, max_tokens=max_tokens)
        raise RuntimeError("Missing OPENROUTER_API_KEY and local fallback disabled.")

    default_system = (
        "You are a deterministic code formatting and editing assistant. "
        "Perform the requested mechanical edit strictly and output only the final result "
        "without greeting, conclusion, or commentary."
    )
    messages = [
        {"role": "system", "content": system_prompt if system_prompt is not None else default_system},
        {"role": "user", "content": prompt},
    ]
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/richfrem/agent-plugins-skills",
            "X-Title": "cli-agent micro-tier client",
        },
        method="POST",
    )

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            dur = time.perf_counter() - t0
            res = json.loads(resp.read().decode("utf-8"))
            content = res["choices"][0]["message"]["content"]
            usage = res.get("usage", {})
            p_tok = usage.get("prompt_tokens", len(prompt) // 4)
            c_tok = usage.get("completion_tokens", len(content) // 4)
            cost = calculate_cost(model, p_tok, c_tok)
            record_spend(cost)
            return MicroTierResponse(
                content=content,
                model=model,
                prompt_tokens=p_tok,
                completion_tokens=c_tok,
                cost_usd=round(cost, 8),
                latency_s=round(dur, 3),
                fallback_triggered=False,
                status="OK",
            )
    except Exception as e:  # network, HTTP, or malformed body
        dur = time.perf_counter() - t0
        sys.stderr.write(f"[openrouter_client] OpenRouter request failed ({e}).\n")
        if allow_local_fallback:
            fallback = call_local_llm(prompt, max_tokens=max_tokens)
            fallback.status = f"FALLBACK_AFTER_ERROR: {e}"
            return fallback
        return MicroTierResponse(
            content=f"[Error: {e}]",
            model=model,
            prompt_tokens=0,
            completion_tokens=0,
            cost_usd=0.0,
            latency_s=round(dur, 3),
            fallback_triggered=False,
            status=f"FAILED: {e}",
        )


def main() -> None:
    """CLI entry point: run one prompt or print the cumulative spend."""
    parser = argparse.ArgumentParser(description="OpenRouter micro-tier client (cli-agent)")
    parser.add_argument("prompt", nargs="?", help="Prompt to execute")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--system", help="System prompt")
    parser.add_argument("--no-local-fallback", action="store_true", help="Fail instead of using the local server")
    parser.add_argument("--spend", action="store_true", help="Display cumulative spend and exit")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.spend:
        print(f"Cumulative Spend: ${get_cumulative_spend():.6f} / ${monthly_hard_cap_usd():.2f}")
        return
    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    res = invoke_micro_tier(
        prompt=args.prompt,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        system_prompt=args.system,
        allow_local_fallback=not args.no_local_fallback,
    )
    if args.format == "json":
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"=== Micro-Tier Response [{res.model}] ===")
        print(f"Status:     {res.status}")
        print(f"Tokens:     {res.prompt_tokens} in / {res.completion_tokens} out")
        print(f"Cost:       ${res.cost_usd:.8f}")
        print(f"Latency:    {res.latency_s:.3f} s")
        print(f"Fallback:   {res.fallback_triggered}")
        print("--- Output ---")
        print(res.content)


if __name__ == "__main__":
    main()
