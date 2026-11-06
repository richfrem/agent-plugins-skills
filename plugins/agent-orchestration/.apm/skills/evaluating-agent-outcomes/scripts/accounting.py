#!/usr/bin/env python3
"""Generic usage accounting (stdlib only): model cost tiers, a task/usage ledger fold, and turn-budget checks.

Budget POLICY (which subscription profile applies, soft limits) is data supplied by the caller; this module only does the arithmetic.
Lookup rule is the historical one: first table entry whose key is a substring of the model name (or vice versa), default standard 1.0.
"""
import uuid
from datetime import datetime, timezone

MODEL_COST_TIERS = {
    "gpt-6-astra": {"tier": "frontier", "weight": 4.0, "desc": "Frontier Codex Astra (Heavy Architectural Reasoning)"},
    "astra": {"tier": "frontier", "weight": 4.0, "desc": "Frontier Codex Astra"},
    "claude-opus": {"tier": "frontier", "weight": 4.0, "desc": "Frontier Claude Opus (3/4/5/5.5)"},
    "opus": {"tier": "frontier", "weight": 4.0, "desc": "Frontier Claude Opus"},
    "claude-fable": {"tier": "frontier", "weight": 4.5, "desc": "Frontier Claude Fable (5/5.1)"},
    "fable": {"tier": "frontier", "weight": 4.5, "desc": "Frontier Claude Fable"},
    "gemini-4": {"tier": "frontier", "weight": 4.0, "desc": "Frontier Gemini 4"},
    "o1": {"tier": "frontier", "weight": 3.5, "desc": "OpenAI o1 Reasoning"},
    "o3": {"tier": "frontier", "weight": 4.0, "desc": "OpenAI o3 Reasoning"},
    "gpt-6.1-sol": {"tier": "standard", "weight": 1.5, "desc": "Standard Codex Sol 6.1"},
    "sol": {"tier": "standard", "weight": 1.5, "desc": "Standard Codex Sol"},
    "gpt-6-luna": {"tier": "standard", "weight": 1.0, "desc": "Standard Codex Luna 6.0"},
    "luna": {"tier": "standard", "weight": 1.0, "desc": "Standard Codex Luna"},
    "claude-3-5-sonnet": {"tier": "standard", "weight": 1.0, "desc": "Standard Claude Sonnet"},
    "claude-sonnet": {"tier": "standard", "weight": 1.0, "desc": "Standard Claude Sonnet (3.5/4/5/5.5)"},
    "sonnet": {"tier": "standard", "weight": 1.0, "desc": "Standard Claude Sonnet"},
    "gemini-pro": {"tier": "standard", "weight": 1.0, "desc": "Standard Gemini Pro (1.5/2/3/3.1)"},
    "gpt-4o": {"tier": "standard", "weight": 1.0, "desc": "Standard GPT-4o"},
    "claude-3-5-haiku": {"tier": "cheap", "weight": 0.2, "desc": "Fast & Cheap Haiku"},
    "claude-haiku": {"tier": "cheap", "weight": 0.2, "desc": "Fast & Cheap Haiku (3.5/4.5/5.5)"},
    "haiku": {"tier": "cheap", "weight": 0.2, "desc": "Fast & Cheap Haiku"},
    "gemini-3.8-flash": {"tier": "cheap", "weight": 0.1, "desc": "Fast & Cheap Gemini 3.8 Flash"},
    "gemini-flash": {"tier": "cheap", "weight": 0.1, "desc": "Fast & Cheap Gemini Flash (1.5/2/3.6/3.7/3.8)"},
    "flash": {"tier": "cheap", "weight": 0.1, "desc": "Fast & Cheap Gemini Flash"},
    "gpt-4o-mini": {"tier": "cheap", "weight": 0.15, "desc": "Fast & Cheap Mini"},
    "mini": {"tier": "cheap", "weight": 0.15, "desc": "Fast & Cheap Mini"},
    "local-llama": {"tier": "free", "weight": 0.05, "desc": "Local Offline LLM / Qwen2"},
    "llama": {"tier": "free", "weight": 0.05, "desc": "Local Offline LLM"},
    "qwen": {"tier": "free", "weight": 0.05, "desc": "Local Offline Qwen2"},
}


def get_model_tier(model_name, table=None):
    clean = model_name.lower().strip()
    for k, v in (table or MODEL_COST_TIERS).items():
        if k in clean or clean in k:
            return v
    return {"tier": "standard", "weight": 1.0, "desc": f"Standard ({model_name})"}


def get_model_cost_weight(model_name, table=None):
    return get_model_tier(model_name, table)["weight"]


def new_ledger(now=None):
    return {"schema_version": 1, "updated_at": now or datetime.now(timezone.utc).isoformat(), "total_tokens_consumed": 0,
            "total_turns": 0, "tasks": {}, "recent_records": []}


def fold_usage(data, entry, recent_limit=30, now=None):
    """Apply one usage record {task_id, backend, model, tokens_est, turns, ...extras} to the ledger in place.
    Returns (record_entry, task_stat). Extras (measured fields) are passed through untouched."""
    t = data.setdefault("tasks", {}).setdefault(entry["task_id"], {"tokens_consumed": 0, "turns": 0, "last_backend": entry["backend"], "last_model": entry["model"]})
    t["tokens_consumed"] += entry["tokens_est"]
    t["turns"] += entry["turns"]
    t["last_backend"], t["last_model"] = entry["backend"], entry["model"]
    data["total_tokens_consumed"] = data.get("total_tokens_consumed", 0) + entry["tokens_est"]
    data["total_turns"] = data.get("total_turns", 0) + entry["turns"]
    stamp = now or datetime.now(timezone.utc).isoformat()
    data["updated_at"] = stamp
    rec = {"record_id": str(uuid.uuid4()), "timestamp": stamp, **entry}
    recent = data.setdefault("recent_records", [])
    recent.insert(0, rec)
    data["recent_records"] = recent[:recent_limit]
    return rec, t


def check_turns(profiles, name, planned_turns):
    """Policy lives in `profiles` (caller data). -> result dict; unknown profile falls back to 'default'."""
    prof = profiles.get(name, profiles["default"])
    limit = prof["soft_turn_limit_per_task"]
    ok = planned_turns <= limit
    return {"profile": name, "description": prof["description"], "planned_turns": planned_turns, "soft_turn_limit": limit,
            "status": "APPROVED" if ok else "WARNING",
            "warning": "" if ok else f"Planned turns ({planned_turns}) exceeds soft limit ({limit}) for {name}."}


# ---------------------------------------------------------------- work-item budgets and attempt accounting (MISSION-055 hardening)
BUDGET_KEYS = {"max_attempts", "max_tokens", "per_attempt_token_reserve"}


def _posint(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def validate_budget(b):
    """Semantics (all limits apply PER WORK ITEM, summed over every execution unit, backend and fallback attempt of that item):
      max_attempts              required positive integer - maximum EXECUTION attempts (preflight refusals and evaluation calls do not count)
      max_tokens                optional positive integer - ceiling on tokens measured/charged across all attempts of the item
      per_attempt_token_reserve optional positive integer <= max_tokens - tokens charged for an attempt whose usage is unknown or
                                not yet known (running). It is an ADMISSION control, not a backend-enforced cap.
    Negative, zero, float, boolean, string or unknown keys are rejected. Returns a list of problems."""
    if not isinstance(b, dict):
        return ["budget must be an object"]
    p = [f"unsupported budget key '{k}'" for k in sorted(set(b) - BUDGET_KEYS)]
    if "max_attempts" not in b:
        p.append("budget.max_attempts is required")
    for k in ("max_attempts", "max_tokens", "per_attempt_token_reserve"):
        if k in b and not _posint(b[k]):
            p.append(f"budget.{k} must be a positive integer (not boolean/float/string): got {b[k]!r}")
    if _posint(b.get("per_attempt_token_reserve")) and _posint(b.get("max_tokens")) and b["per_attempt_token_reserve"] > b["max_tokens"]:
        p.append("budget.per_attempt_token_reserve exceeds budget.max_tokens")
    if "per_attempt_token_reserve" in b and "max_tokens" not in b:
        p.append("budget.per_attempt_token_reserve is meaningless without budget.max_tokens")
    return p


def summarize_attempts(records):
    """Fold an append-only attempt ledger. Records: {kind:'attempt', attempt_id, unit, state: reserved|finished|refused_preflight,
    backend_attempts:[{backend,status,usage:{total_tokens}}], reserve_tokens} and {kind:'evaluation', eval_id, model_tokens}.
    The LAST record per attempt_id wins, so the same attempt is never counted twice. Unknown usage stays unknown; known totals are
    reported as lower bounds when anything is unknown."""
    latest, evals = {}, {}
    for r in records:
        if r.get("kind") == "attempt" and r.get("attempt_id"):
            latest[r["attempt_id"]] = r
        elif r.get("kind") == "evaluation" and r.get("eval_id"):
            evals[r["eval_id"]] = r
    exec_attempts = [r for r in latest.values() if r.get("state") in ("reserved", "finished")]
    refused = [r for r in latest.values() if r.get("state") == "refused_preflight"]
    known, unknown, backend_n, running, reserve_running = 0, 0, 0, 0, 0
    for r in exec_attempts:
        if r["state"] == "reserved":
            running += 1
            reserve_running += r.get("reserve_tokens") or 0
            continue
        seen = set()
        for i, ba in enumerate(r.get("backend_attempts") or [{"usage": {"total_tokens": None}}]):
            key = (r["attempt_id"], i)
            if key in seen:
                continue
            seen.add(key); backend_n += 1
            t = (ba.get("usage") or {}).get("total_tokens")
            if isinstance(t, int) and not isinstance(t, bool) and t >= 0:
                known += t
            else:
                unknown += 1
    eval_known = sum(e["model_tokens"] for e in evals.values() if isinstance(e.get("model_tokens"), int))
    return {"execution_attempts": len(exec_attempts), "running_or_unfinished": running, "preflight_refusals": len(refused),
            "evaluation_calls": len(evals), "evaluation_tokens_known": eval_known,
            "backend_attempts": backend_n, "execution_tokens_known": known, "backend_attempts_with_unknown_usage": unknown,
            "execution_tokens_is_lower_bound": unknown > 0 or running > 0, "reserved_for_running": reserve_running}


def admit(budget, summary):
    """May ONE more execution attempt launch? Pure decision over the validated budget and summarize_attempts() output.
    Policy for incomplete measurements: with a token ceiling, an attempt whose usage is unknown (or still running) is charged
    budget.per_attempt_token_reserve; if no reserve is declared, further launches are refused rather than assuming zero."""
    bad = validate_budget(budget)
    if bad:
        return {"ok": False, "reason": "invalid budget: " + "; ".join(bad), "reserve_tokens": None}
    if summary["execution_attempts"] >= budget["max_attempts"]:
        return {"ok": False, "reason": f"attempt budget exhausted ({summary['execution_attempts']}/{budget['max_attempts']})", "reserve_tokens": None}
    mt, res = budget.get("max_tokens"), budget.get("per_attempt_token_reserve")
    if mt is None:
        return {"ok": True, "reason": "no token ceiling declared", "reserve_tokens": None}
    unknown_or_running = summary["backend_attempts_with_unknown_usage"] + summary["running_or_unfinished"]
    if unknown_or_running and res is None:
        return {"ok": False, "reserve_tokens": None, "reason": "token ceiling declared but usage of earlier/running attempts is unknown and no "
                "budget.per_attempt_token_reserve was declared; refusing rather than assuming zero cost"}
    committed = summary["execution_tokens_known"] + (res or 0) * summary["backend_attempts_with_unknown_usage"] + \
        (summary["reserved_for_running"] if summary["running_or_unfinished"] else 0)
    need = res or 0
    if committed >= mt or committed + need > mt:
        return {"ok": False, "reserve_tokens": None, "reason": f"token budget exhausted (committed {committed} + reserve {need} > {mt})"}
    return {"ok": True, "reserve_tokens": res, "reason": "within budget"}


# ---------------------------------------------------------------- P02 measurement observations (agent-agentic-os control plane schema)
import os as _os, time as _time, importlib.util as _ilu
from pathlib import Path as _Path

P02_KIND, P02_VERSION = "p0_measurement_observation", "1.0-draft"


def uuid7():
    """RFC 9562 UUIDv7 (the P02 schema requires it for event ids)."""
    ms = int(_time.time() * 1000)
    b = bytearray(ms.to_bytes(6, "big") + _os.urandom(10))
    b[6] = (b[6] & 0x0F) | 0x70
    b[8] = (b[8] & 0x3F) | 0x80
    h = bytes(b).hex()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def find_p02(extra_roots=()):
    """Locate the control plane's measurement module (agent-agentic-os / running-control-plane) if it is installed; optional."""
    rel = _Path("running-control-plane/scripts/control_plane/measurement.py")
    here = _Path(__file__).resolve()
    cands = [_Path(r) / rel for r in extra_roots] + [here.parents[2] / rel, _Path.home() / ".claude/skills" / rel, _Path.home() / ".agents/skills" / rel]
    for c in cands:
        if c.is_file():
            spec = _ilu.spec_from_file_location("_p02_measurement", c)
            mod = _ilu.module_from_spec(spec)
            import sys as _sys
            _sys.modules["_p02_measurement"] = mod            # dataclasses need the module registered
            spec.loader.exec_module(mod)
            return mod
    return None


def to_measurement_observation(work_id, attempt_id, backend_index, backend_attempt, run_id, requested_model=None, runtime_version=None, p02=None):
    """Map ONE backend attempt of the attempt ledger to the control plane's closed P02 observation schema so both systems share one
    measurement vocabulary (null vs zero, provenance, no prompt/output text). Mapping notes:
      * input_tokens = all input-side tokens incl. cache reads/writes (P02: cached_tokens is a SUBSET of input), cached_tokens = cache reads;
      * the budgeted total used by accounting.admit (input + output + cache-write) is NOT a P02 field and stays in the ledger;
      * a vendor-reported total without a split cannot be represented (P02 has no total slot) -> provenance 'reported', tokens null, reason stated;
      * digest: computed with the control plane's own canonicalizer when installed, else a draft fixture with null digest + reason."""
    u = backend_attempt.get("usage") or {}
    ts = lambda t: _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime(t))
    ended = backend_attempt.get("ended") or _time.time()
    dur = max(0, int(((backend_attempt.get("ended") or ended) - (backend_attempt.get("started") or ended)) * 1000))
    src = (u.get("source") or "")
    if u.get("tokens_out") is not None and "transcript" in src:
        tin = (u.get("tokens_in") or 0) + (u.get("cache_write") or 0) + (u.get("cache_read") or 0)
        usage = {"provenance": "measured", "input_tokens": tin, "output_tokens": u["tokens_out"], "cached_tokens": u.get("cache_read") or 0,
                 "reasoning_tokens": None, "unavailable_reason": "reasoning tokens are not reported separately by the source", "scope": "final"}
    elif u.get("tokens_in") is not None and u.get("tokens_out") is not None:
        usage = {"provenance": "reported", "input_tokens": u["tokens_in"], "output_tokens": u["tokens_out"], "cached_tokens": None, "reasoning_tokens": None,
                 "unavailable_reason": "cached and reasoning tokens not reported", "scope": "final"}
    elif isinstance(u.get("total_tokens"), int):
        usage = {"provenance": "reported", "input_tokens": None, "output_tokens": None, "cached_tokens": None, "reasoning_tokens": None,
                 "unavailable_reason": f"only a combined total ({u['total_tokens']}) was reported; P02 has no total-only field", "scope": "final"}
    else:
        usage = {"provenance": "unavailable", "input_tokens": None, "output_tokens": None, "cached_tokens": None, "reasoning_tokens": None,
                 "unavailable_reason": u.get("source") or "backend reported no usage and no transcript attribution was possible", "scope": "final"}
    obs = {"artifact_kind": P02_KIND, "schema_version": P02_VERSION,
           "capture": {"method": "orchestrator-attempt-ledger", "captured_at_utc": ts(_time.time()), "source_runtime": backend_attempt.get("backend") or "unknown",
                       **({"source_runtime_version": runtime_version} if runtime_version else {"source_runtime_version": None, "source_runtime_version_unavailable_reason": "executor result carried no version"}),
                       "sanitization": "ids, counts, timings and model names only; no prompt, output or environment text"},
           "producer": {"namespace": "orchestrating-agent-work.work_loop", "version": "1", "install_fingerprint": None,
                        "install_fingerprint_unavailable_reason": "not computed by the loop"},
           "correlation": {"task_id": work_id, "task_generation_id": work_id, "run_id": run_id, "invocation_id": attempt_id, "attempt_id": f"{attempt_id}.b{backend_index}"},
           "event": {"event_id": uuid7(), "occurred_at_utc": ts(ended), "coverage_state": "observed", "canonical_digest": None,
                     "canonical_digest_unavailable_reason": "digest not computed (control plane measurement module not installed)"},
           "execution": {"exit_code": 0 if backend_attempt.get("status") == "ok" else (backend_attempt.get("exit") if isinstance(backend_attempt.get("exit"), int) else 1),
                         "duration_ms": dur, "duration_provenance": "measured", "requested_model": requested_model or backend_attempt.get("backend") or "unknown",
                         "observed_model": None, "observed_model_unavailable_reason": "CLI text mode does not report the model actually used"},
           "usage": usage}
    p02 = find_p02() if p02 is None else p02
    if p02:
        base_event = {k: v for k, v in obs["event"].items() if k not in ("canonical_digest", "canonical_digest_unavailable_reason")}
        try:
            digest = p02.compute_canonical_digest({**obs, "event": base_event})       # the control plane's own canonicalizer (it drops canonical_digest)
            obs["event"] = {**base_event, "canonical_digest": digest}
        except Exception:  # noqa: BLE001 - keep the draft-fixture form (null digest + reason)
            pass
    return obs
