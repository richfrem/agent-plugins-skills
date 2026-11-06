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
