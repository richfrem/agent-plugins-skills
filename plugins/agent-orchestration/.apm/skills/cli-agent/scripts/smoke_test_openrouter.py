#!/usr/bin/env python3
"""smoke_test_openrouter.py - Live end-to-end check of the OpenRouter micro-tier path.

Runs one task spec (test-matrix shape) through the JEV router and the
OpenRouter client against the pinned cheap model, then verifies:
routing matches the spec, the live call succeeded without fallback, the
output equals the expected JSON, and the spend ledger incremented.

Costs about $0.00001 per run. Skips (exit 0, message) when no
OPENROUTER_API_KEY is available, so it is safe in CI.

Key Input Dependencies:
    jev_router.py, openrouter_client.py (same directory)
    references/openrouter-smoke-task.json (default spec)

Function Index:
    run_smoke - execute the spec and print PASS/FAIL per check; returns exit code
    main      - CLI entry point (--task <spec.json>)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
DEFAULT_TASK = os.path.join(SCRIPT_DIR, "..", "references", "openrouter-smoke-task.json")


def run_smoke(task_path: str) -> int:
    """Route, call, verify. Returns 0 on PASS, 1 on FAIL, 0 with a skip note when no key."""
    from jev_router import JEVRouter
    import openrouter_client as oc

    if not oc.get_api_key():
        print("SKIP: no OPENROUTER_API_KEY available; live smoke not run.")
        return 0

    with open(task_path, "r", encoding="utf-8") as f:
        task = json.load(f)

    router = JEVRouter()
    router.route_task("warmup")
    d = router.route_task(task["description"])
    print(f"[route] tier={d.tier} runtime={d.recommended_runtime} model={d.recommended_model} "
          f"class={d.complexity_class} tokens={d.tokens_consumed} latency={d.latency_ms:.3f}ms")
    route_ok = d.tier == task["expected_tier"] and d.complexity_class == task["expected_complexity"]

    before = oc.get_cumulative_spend()
    res = oc.invoke_micro_tier(task["description"], model=task["recommended_model"],
                               max_tokens=100, allow_local_fallback=False)
    after = oc.get_cumulative_spend()
    print(f"[call]  status={res.status} model={res.model} tokens={res.prompt_tokens}in/{res.completion_tokens}out "
          f"cost=${res.cost_usd:.8f} latency={res.latency_s}s fallback={res.fallback_triggered}")
    print(f"[out]   {res.content!r}")

    m = re.search(r"\{.*\}", res.content, re.S)
    parsed = None
    if m:
        try:
            parsed = json.loads(m.group(0))
        except ValueError:
            parsed = None
    out_ok = parsed == task["expected_output"] and isinstance(parsed, dict) and list(parsed) == sorted(parsed)
    live_ok = res.status == "OK" and not res.fallback_triggered
    ledger_ok = after > before

    print(f"[spend] ledger {before:.8f} -> {after:.8f} (cap ${oc.monthly_hard_cap_usd():.2f})")
    print(f"[verify] route={'PASS' if route_ok else 'FAIL'} output={'PASS' if out_ok else 'FAIL'} "
          f"live_openrouter={'PASS' if live_ok else 'FAIL'} ledger_incremented={'PASS' if ledger_ok else 'FAIL'}")
    return 0 if (route_ok and out_ok and live_ok and ledger_ok) else 1


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Live OpenRouter micro-tier smoke test")
    parser.add_argument("--task", default=DEFAULT_TASK, help="Task spec JSON (test-matrix shape)")
    args = parser.parse_args()
    sys.exit(run_smoke(args.task))


if __name__ == "__main__":
    main()
