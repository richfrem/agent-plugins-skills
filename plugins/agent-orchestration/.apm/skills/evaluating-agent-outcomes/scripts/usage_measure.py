#!/usr/bin/env python3
"""Generic usage MEASUREMENT (stdlib only): zero-token vendor usage snapshots/diffs, transcript and rollout token readers,
secret scrubbing and catalog-priced dollar cost. Extracted verbatim from Sanctuary's usage_probe.py (MISSION-055); the
single authoritative implementation. Policy (floors, ceilings, predictors, ledgers) stays with the consumer.
Catalogs come from the installed cli-agent skill (env AGENT_CLI_REFERENCES, legacy SANCTUARY_CLI_AGENT_REFERENCES).
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{6,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|secret)\"?\s*[:=]\s*\"?[A-Za-z0-9._\-]{16,}"),
    re.compile(r"(?i)hf_[A-Za-z0-9]{20,}"),
]


def assert_no_secrets(obj: Any) -> None:
    """Raise ValueError if any credential-looking string appears in obj (serialised)."""
    blob = json.dumps(obj, default=str)
    for pat in SECRET_PATTERNS:
        if pat.search(blob):
            raise ValueError(f"credential-like pattern in usage record ({pat.pattern[:24]}...)")


def parse_claude_usage(text: str) -> Dict[str, Any]:
    """Parse headless `claude -p /usage` text into session (5-hour) and weekly percent used."""
    out: Dict[str, Any] = {"session_pct_used": None, "session_resets": None,
                           "week_pct_used": None, "week_resets": None}
    # The reset suffix is optional: the CLI omits "· resets ..." for some windows (observed for
    # "Current session: 0% used"). The displayed percentage is kept as displayed; an absent
    # reset is recorded as None, never as a zero or an imputed value.
    m = re.search(r"Current session:\s*(\d+)%\s*used(?:\s*[·\-]\s*resets\s*(.+))?", text)
    if m:
        out["session_pct_used"] = int(m.group(1))
        out["session_resets"] = m.group(2).strip() if m.group(2) else None
    m = re.search(r"Current week \(all models\):\s*(\d+)%\s*used(?:\s*[·\-]\s*resets\s*(.+))?", text)
    if m:
        out["week_pct_used"] = int(m.group(1))
        out["week_resets"] = m.group(2).strip() if m.group(2) else None
    return out


def parse_agy_usage(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse `agy -p /usage --output-format json` into one row per quota bucket."""
    rows: List[Dict[str, Any]] = []
    groups = (((obj or {}).get("command") or {}).get("data") or {}).get("groups") or []
    for g in groups:
        for b in g.get("buckets") or []:
            frac = b.get("remaining_fraction")
            if frac is None:
                continue
            window = b.get("window") if b.get("window") in ("weekly", "5h") else "other"
            rows.append({"group": g.get("name", ""), "bucket": b.get("name", ""), "window": window,
                         "remaining_pct": round(float(frac) * 100.0, 3), "resets_at": b.get("reset_time", "")})
    return rows


def reported_tokens(backend: str, obj: Dict[str, Any]) -> int:
    """Tokens the CLI itself reports for a headless call (used to assert probes cost 0)."""
    u = (obj or {}).get("usage") or {}
    if backend == "agy":
        return int(u.get("total_tokens", 0) or 0)
    if backend == "claude":
        return int(u.get("input_tokens", 0) or 0) + int(u.get("output_tokens", 0) or 0)
    return 0


def read_codex_latest(sessions_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Newest rollout that has a token_count event; returns window percents and session totals.

    Scans newest-first because TUI-only sessions write rollouts with no token_count. Reads only
    rollout-*.jsonl under sessions_dir; never opens auth files.
    """
    sessions_dir = sessions_dir or Path.home() / ".codex" / "sessions"
    files = sorted(sessions_dir.glob("**/rollout-*.jsonl"), reverse=True)
    for f in files[:40]:
        last = None
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    if '"token_count"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    if (rec.get("payload") or {}).get("type") == "token_count":
                        last = rec
        except OSError:
            continue
        if last is None:
            continue
        p = last["payload"]
        rl = p.get("rate_limits") or {}
        tot = ((p.get("info") or {}).get("total_token_usage")) or {}
        return {
            "five_hour_pct_used": (rl.get("primary") or {}).get("used_percent"),
            "weekly_pct_used": (rl.get("secondary") or {}).get("used_percent"),
            "five_hour_resets_at": (rl.get("primary") or {}).get("resets_at"),
            "weekly_resets_at": (rl.get("secondary") or {}).get("resets_at"),
            "session_total_tokens": tot.get("total_tokens"),
            "source_timestamp": last.get("timestamp"),
            "source_file": f.name,
        }
    return None


def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def claude_tokens_between(project_dir: Path, start: str, end: str,
                          own_session: Optional[str] = None) -> Dict[str, Any]:
    """Sum assistant-message token usage in [start, end] across Claude transcripts.

    concurrent=True when a transcript other than own_session wrote messages in the interval
    (window-percent deltas are then shared with that activity and must be treated as noisy).
    """
    t0, t1 = _parse_ts(start), _parse_ts(end)
    tot = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0,
           "cache_read_input_tokens": 0, "cache_write_1h_tokens": 0}
    active = set()
    for f in project_dir.glob("*.jsonl"):
        sid = f.stem
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    if '"usage"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    ts = _parse_ts(rec.get("timestamp", ""))
                    usage = (rec.get("message") or {}).get("usage")
                    if not ts or not usage or not (t0 <= ts <= t1):
                        continue
                    active.add(sid)
                    if own_session is None or sid == own_session:
                        for k in tot:
                            tot[k] += int(usage.get(k, 0) or 0)
                        tot["cache_write_1h_tokens"] += int((usage.get("cache_creation") or {}).get("ephemeral_1h_input_tokens", 0) or 0)
        except OSError:
            continue
    # Without a known own session, two or more active transcripts means shared activity.
    others = active - {own_session} if own_session else (active if len(active) > 1 else set())
    return {**tot, "concurrent": bool(others), "other_active_sessions": len(others)}


def parse_agy_json_usage(raw: str) -> Optional[Dict[str, int]]:
    """Token usage from `agy -p ... --output-format json` output; None for text output, failures or no usage block.

    total_tokens excludes cache_read_tokens (it is input + output + thinking)."""
    try:
        d = json.loads(raw)
        if d.get("status") != "SUCCESS":
            return None
        u = d["usage"]
        return {"total_tokens": int(u["total_tokens"]), "input_tokens": int(u.get("input_tokens", 0)),
                "output_tokens": int(u.get("output_tokens", 0)), "cache_read_tokens": int(u.get("cache_read_tokens", 0))}
    except (ValueError, KeyError, TypeError, AttributeError):
        return None


def codex_tokens_between(sessions_dir: Optional[Path], start: str, end: str) -> Dict[str, Any]:
    """Codex tokens used in [start, end]: per rollout, the cumulative totals at the end minus the totals at start.

    Returns total_tokens plus the split input_tokens / cached_input_tokens / output_tokens (codex's input_tokens
    includes the cached part). A session that began inside the interval counts from zero. concurrent=True when more
    than one rollout recorded token usage in the interval (window percents are then shared and must be treated as noisy).
    """
    sessions_dir = sessions_dir or Path.home() / ".codex" / "sessions"
    t0, t1 = _parse_ts(start), _parse_ts(end)
    keys = ("total_tokens", "input_tokens", "cached_input_tokens", "output_tokens")
    sums = {k: 0 for k in keys}
    active = 0
    for f in sessions_dir.glob("**/rollout-*.jsonl"):
        before = None
        last_in = None
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    if '"token_count"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    p = rec.get("payload") or {}
                    ts = _parse_ts(rec.get("timestamp", ""))
                    use = (p.get("info") or {}).get("total_token_usage") or {}
                    if p.get("type") != "token_count" or ts is None or use.get("total_tokens") is None:
                        continue
                    if ts < t0:
                        before = use
                    elif ts <= t1:
                        last_in = use
        except OSError:
            continue
        if last_in is not None:
            for k in keys:
                sums[k] += max(0, (last_in.get(k) or 0) - ((before or {}).get(k) or 0))
            active += 1
    return {**sums, "concurrent": active > 1, "active_sessions": active}


def _run(argv: List[str], timeout: int = 60) -> str:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=True).stdout


def snapshot(backends: List[str], runner: Callable[..., str] = _run, now: Optional[str] = None,
             codex_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Collect a usage snapshot. Every collector is zero-token; failures degrade to 'unavailable'."""
    now = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snap: Dict[str, Any] = {"timestamp": now, "backends": {}}
    for b in backends:
        try:
            if b == "claude":
                data = parse_claude_usage(runner(["claude", "-p", "/usage"]))
                data["status"] = "ok" if data["session_pct_used"] is not None else "unparsed"
            elif b == "agy":
                raw = json.loads(runner(["agy", "-p", "/usage", "--output-format", "json"]))
                tokens = reported_tokens("agy", raw)
                rows = parse_agy_usage(raw)
                data = {"status": "ok" if rows else "unparsed", "buckets": rows, "probe_tokens": tokens}
                if tokens:
                    data["status"] = "probe_cost_nonzero"
            elif b == "codex":
                r = read_codex_latest(codex_dir)
                data = {"status": "ok", **r} if r else {"status": "unavailable"}
            else:
                data = {"status": "unsupported"}
        except Exception as exc:  # noqa: BLE001 - probes must never crash the orchestrator
            data = {"status": "unavailable", "error": type(exc).__name__}
        snap["backends"][b] = data
    assert_no_secrets(snap)
    return snap


def diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """Window deltas between two snapshots, per backend."""
    out: Dict[str, Any] = {"from": before["timestamp"], "to": after["timestamp"]}
    bb, ab = before["backends"], after["backends"]
    if "claude" in bb and "claude" in ab:
        c0, c1 = bb["claude"], ab["claude"]

        def d(k):
            return None if c0.get(k) is None or c1.get(k) is None else c1[k] - c0[k]
        out["claude"] = {"session_pct_delta": d("session_pct_used"), "week_pct_delta": d("week_pct_used")}
    if "agy" in bb and "agy" in ab:
        idx = {(r["group"], r["window"]): r for r in bb["agy"].get("buckets", [])}
        rows = []
        for r in ab["agy"].get("buckets", []):
            prev = idx.get((r["group"], r["window"]))
            if prev:
                rows.append({"group": r["group"], "window": r["window"],
                             "remaining_pct_delta": round(r["remaining_pct"] - prev["remaining_pct"], 3)})
        out["agy"] = rows
    if "codex" in bb and "codex" in ab:
        x0, x1 = bb["codex"], ab["codex"]

        def dc(k):
            return None if x0.get(k) is None or x1.get(k) is None else round(x1[k] - x0[k], 3)
        out["codex"] = {"five_hour_pct_delta": dc("five_hour_pct_used"), "weekly_pct_delta": dc("weekly_pct_used"),
                        "stale": x0.get("source_timestamp") == x1.get("source_timestamp")}
    return out


CATALOG_DIRS = [
    Path.home() / ".claude" / "skills" / "cli-agent" / "references",
    Path.home() / ".agents" / "skills" / "cli-agent" / "references",
    Path.home() / ".gemini" / "antigravity-cli" / "skills" / "cli-agent" / "references",
]


def find_catalog_dir() -> Optional[Path]:
    """The installed cli-agent skill's model catalogs (single source of truth for prices and capabilities)."""
    env = os.environ.get("AGENT_CLI_REFERENCES") or os.environ.get("SANCTUARY_CLI_AGENT_REFERENCES")
    for d in ([Path(env)] if env else []) + CATALOG_DIRS:
        if (d / "claude-models.json").exists():
            return d
    return None


def load_prices(catalog_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Per-model prices (USD per million tokens) read from the cli-agent catalogs; nothing is duplicated here.

    Keys are exact cli_ids from claude/codex/agy catalogs (direct API prices); Copilot entries are keyed
    'copilot:<cli_id>' and carry credits_per_mtok. A model absent from the catalog is simply absent:
    callers get None, never a price borrowed from a similarly named model.
    """
    catalog_dir = catalog_dir or find_catalog_dir()
    out: Dict[str, Any] = {}
    if catalog_dir is None:
        return out
    for fname, prefix in (("claude-models.json", ""), ("codex-models.json", ""), ("agy-models.json", ""), ("copilot-models.json", "copilot:")):
        try:
            cat = json.loads((catalog_dir / fname).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        meta = cat.get("_meta", {})
        for m in cat.get("models", []):
            pr = m.get("pricing_usd_per_1m") or {}
            entry = {"input_per_mtok": pr.get("input"), "output_per_mtok": pr.get("output"),
                     "cached_input_per_mtok": pr.get("cached_input"), "cache_write_per_mtok": pr.get("cache_write"),
                     "cache_write_1h_per_mtok": pr.get("cache_write_1h"),
                     "credits_per_mtok": m.get("credits_per_1m"), "status": m.get("status"),
                     "catalog": fname, "catalog_updated": meta.get("updated")}
            out.setdefault(prefix + m["cli_id"], entry)
    return out


def cost_usd(model: str, tokens_in: int, tokens_out: int, prices: Optional[Dict[str, Any]] = None,
             cache_read: int = 0, cache_write: int = 0, cache_write_1h: int = 0) -> Optional[float]:
    """Dollar cost for an EXACT catalog model id; None when absent or any needed price is null (never guessed).

    tokens_in excludes cache reads/writes, which are priced at their own catalog rates: cache_write is the
    5-minute TTL write, cache_write_1h the 1-hour TTL write (Claude Code uses the 1-hour TTL).
    """
    prices = load_prices() if prices is None else prices
    p = prices.get(model)
    if not p or p.get("input_per_mtok") is None or p.get("output_per_mtok") is None:
        return None
    total = tokens_in / 1e6 * p["input_per_mtok"] + tokens_out / 1e6 * p["output_per_mtok"]
    for tokens, key in ((cache_read, "cached_input_per_mtok"), (cache_write, "cache_write_per_mtok"),
                        (cache_write_1h, "cache_write_1h_per_mtok")):
        if tokens:
            if p.get(key) is None:
                return None
            total += tokens / 1e6 * p[key]
    return round(total, 6)


