#!/usr/bin/env python3
"""
Smoke test: send two identical requests through the proxy, verify the second is faster.

Purpose:
    Live end-to-end check that the KV-cache proxy actually restores a saved
    slot on a repeated prompt instead of re-prefilling from scratch.

Key Input Dependencies:
    - A running llama-server with --slot-save-path (see run_server.py)
    - A running routing proxy with KV-cache logging enabled (see enable_global_routing.py)

Usage:
    python3 smoke_test_kv_cache.py

Environment overrides:
    PROXY_URL   default http://localhost:4000
    PROXY_LOG   default ~/.claude/proxy/logs/proxy.log

PASS criteria (all must hold):
  1. Both requests return HTTP 200
  2. Second request completes faster than first (restored slot vs cold prefill)
  3. Proxy log contains "[kv-cache] MISS" on or before first request
  4. Proxy log contains "[kv-cache] HIT" after first request

Expected llama-server log strings:
  - Slot restored: "restoring context checkpoint"
  - Cache hit prefill: n_tokens = 1 (or very small), progress ≈ 0.0
  - Cold prefill:  n_tokens = <full count>,   progress = 1.0

Prerequisites:
    ./run_server.sh          (llama-server on :8089 with --slot-save-path)
    ./enable_global_routing.sh  (proxy on :4000)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:4000")
PROXY_LOG = os.path.expanduser(
    os.environ.get("PROXY_LOG", "~/.claude/proxy/logs/proxy.log")
)

SYSTEM_PROMPT = "You are a smoke-test assistant. Reply with exactly one word."
REQUEST_BODY = {
    "model": "gemma-4-12b",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Say the word 'ready'."},
    ],
    "max_tokens": 5,
    "stream": False,
}


def _send(label: str) -> tuple[float, int, str]:
    """POST the fixed smoke-test request to the proxy and return (elapsed_seconds, status, body)."""
    payload = json.dumps(REQUEST_BODY).encode("utf-8")
    req = urllib.request.Request(
        f"{PROXY_URL}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print(f"[smoke] {label}...", flush=True)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            elapsed = time.monotonic() - start
            body = resp.read().decode("utf-8")
            return elapsed, resp.status, body
    except urllib.error.HTTPError as e:
        elapsed = time.monotonic() - start
        return elapsed, e.code, e.read().decode("utf-8")
    except Exception as e:
        elapsed = time.monotonic() - start
        return elapsed, -1, str(e)


def _tail_log(path: str, n: int = 100) -> list[str]:
    """Return the last n lines of the log file at path, or an empty list if it can't be read."""
    try:
        with open(path, "r") as f:
            return [line.rstrip() for line in f.readlines()[-n:]]
    except Exception:
        return []


def _check(label: str, condition: bool, detail: str = "") -> bool:
    """Print a PASS/FAIL line for one verdict check and return the condition unchanged."""
    mark = "PASS" if condition else "FAIL"
    msg = f"  {mark}  {label}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    return condition


def _analyze_kv_log(log_before_first: int) -> tuple[bool, bool]:
    """Print new KV-cache log lines since the run started; return (miss_found, hit_found)."""
    all_log = _tail_log(PROXY_LOG, 500)
    new_log = all_log[log_before_first:]
    kv_lines = [l for l in new_log if "[kv-cache]" in l]

    print()
    print("[smoke] KV cache log lines (new this run):")
    for line in kv_lines or ["  (none found)"]:
        print(f"  {line}")

    miss_found = any("MISS" in l for l in kv_lines)
    hit_found = any("HIT" in l for l in kv_lines)
    return miss_found, hit_found


def _print_verdicts(status1: int, status2: int, elapsed1: float, elapsed2: float, miss_found: bool, hit_found: bool) -> bool:
    """Print each PASS/FAIL check and the overall RESULT line; return True if all checks passed."""
    print()
    results = [
        _check("request 1 returned 200",  status1 == 200),
        _check("request 2 returned 200",  status2 == 200),
        _check(
            "second request faster than first",
            elapsed2 < elapsed1,
            f"{elapsed2:.2f}s < {elapsed1:.2f}s" if elapsed2 < elapsed1
            else f"{elapsed2:.2f}s >= {elapsed1:.2f}s — cache may not be working",
        ),
        _check(
            "MISS logged (first request saved slot)",
            miss_found,
            "" if miss_found else "check proxy KV cache is enabled",
        ),
        _check(
            "HIT logged (second request restored slot)",
            hit_found,
            "" if hit_found else "check llama-server started with --slot-save-path",
        ),
    ]

    print()
    if all(results):
        print("RESULT: PASS")
        return True

    print("RESULT: FAIL")
    return False


def main() -> int:
    """Run the two-request KV-cache smoke test against the proxy and print a PASS/FAIL verdict."""
    print(f"[smoke] Proxy : {PROXY_URL}")
    print(f"[smoke] Log   : {PROXY_LOG}")
    print()

    log_before_first = len(_tail_log(PROXY_LOG, 500))

    elapsed1, status1, body1 = _send("Request 1 — expect MISS + save")
    print(f"  → status={status1}  elapsed={elapsed1:.2f}s")
    if status1 != 200:
        print(f"  body: {body1[:400]}")
        print("\nRESULT: FAIL (request 1 did not return 200)")
        return 1

    elapsed2, status2, body2 = _send("Request 2 — expect HIT + restore")
    print(f"  → status={status2}  elapsed={elapsed2:.2f}s")
    if status2 != 200:
        print(f"  body: {body2[:400]}")
        print("\nRESULT: FAIL (request 2 did not return 200)")
        return 1

    miss_found, hit_found = _analyze_kv_log(log_before_first)

    if _print_verdicts(status1, status2, elapsed1, elapsed2, miss_found, hit_found):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
