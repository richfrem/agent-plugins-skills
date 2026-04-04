#!/usr/bin/env python3
"""
Agentic OS - Kernel v3 (triple-loop focused)
Seven commands: acquire_lock, release_lock, emit_event, read_events,
state_update, state_increment, claim_task (partition lock only, no registry).

Deliberately minimal. Solves the triple-loop use case: one ORCHESTRATOR,
one INNER_AGENT (or N agents claiming partitions), one laptop.
"""
import os, sys, json, time, uuid, random, argparse
from pathlib import Path
from datetime import datetime, timezone

KERNEL_DIR  = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / "context"
EVENTS_FILE = KERNEL_DIR / "events.jsonl"
LOCKS_DIR   = KERNEL_DIR / ".locks"
STATE_FILE  = KERNEL_DIR / "os-state.json"
AGENTS_FILE = KERNEL_DIR / "agents.json"
AGENTS_DIR  = KERNEL_DIR / "agents"
EVENTS_MAX_BYTES = 10 * 1024 * 1024  # 10 MB before rotation

# Keys that cannot be overwritten via state_update (prompt injection defense)
PROTECTED_STATE_KEYS = frozenset({"execution_mode", "hook_sample_rate"})


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path, default):
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, just can't signal it


def _is_stale(lock_path):
    """Lease-based stale check: dead PID > expired TTL > mtime fallback."""
    meta = _load(lock_path / "meta.json", {})
    if meta:
        if meta.get("pid") and not _pid_alive(meta["pid"]):
            return True
        if meta.get("expires_at", 0) < time.time():
            return True
        return False
    # Legacy lock without metadata — use mtime
    try:
        timeout = _load(STATE_FILE, {}).get("lock_timeout_seconds", 1800)
        return time.time() - lock_path.stat().st_mtime > timeout
    except OSError:
        return True


def _clear(lock_path):
    """Remove all files in lock dir then rmdir."""
    try:
        for f in Path(lock_path).iterdir():
            f.unlink()
        os.rmdir(lock_path)
    except OSError:
        pass


def _spinlock(lock_path, timeout=30):
    """Directory spinlock. Returns True on success."""
    os.makedirs(LOCKS_DIR, exist_ok=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.mkdir(lock_path)
            return True
        except FileExistsError:
            try:
                if time.time() - Path(lock_path).stat().st_mtime > 20:
                    _clear(lock_path)
            except OSError:
                pass
            time.sleep(random.uniform(0.05, 0.15))
    return False


def _validate_agent(name):
    r = _load(AGENTS_FILE, {})
    if name in r.get("permitted_agents", []):
        return True
    print(f"[Kernel] Unregistered agent: {name}", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def acquire_lock(name, ttl=None):
    lock = LOCKS_DIR / f"{name}.lock"
    os.makedirs(LOCKS_DIR, exist_ok=True)
    if lock.exists():
        if _is_stale(lock):
            _clear(lock)
            print(f"[Kernel] Stale lock cleared: {name}")
        else:
            print(f"[Kernel] Lock busy: {name}", file=sys.stderr)
            sys.exit(1)
    try:
        os.mkdir(lock)
    except FileExistsError:
        print(f"[Kernel] Race on lock: {name}", file=sys.stderr)
        sys.exit(1)
    effective_ttl = ttl or int(_load(STATE_FILE, {}).get("lock_timeout_seconds", 1800))
    try:
        meta = {"pid": os.getpid(), "acquired_at": _now(),
                "expires_at": time.time() + effective_ttl, "ttl": effective_ttl}
        (lock / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    except OSError:
        pass
    print(f"[Kernel] Lock acquired: {name} (ttl={effective_ttl}s)")


def release_lock(name):
    _clear(LOCKS_DIR / f"{name}.lock")
    print(f"[Kernel] Lock released: {name}")


def emit_event(agent, type_, action, status=None, summary=None,
               to=None, correlation_id=None):
    if not _validate_agent(agent):
        sys.exit(1)
    # Rotate if over size limit
    if EVENTS_FILE.exists() and EVENTS_FILE.stat().st_size > EVENTS_MAX_BYTES:
        archive = KERNEL_DIR / "events-archive"
        os.makedirs(archive, exist_ok=True)
        rotate_lock = LOCKS_DIR / "events_rotate.lock"
        try:
            os.mkdir(rotate_lock)
            try:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.rename(EVENTS_FILE, archive / f"events-{ts}.jsonl")
                print(f"[Kernel] Rotated events.jsonl")
            finally:
                _clear(rotate_lock)
        except FileExistsError:
            pass
    event = {"id": str(uuid.uuid4()), "time": _now(),
             "agent": agent, "type": type_, "action": action}
    if to:             event["to"]             = to
    if correlation_id: event["correlation_id"] = correlation_id
    if status:         event["status"]         = status
    if summary:        event["summary"]        = summary
    write_lock = LOCKS_DIR / "events_write.lock"
    if not _spinlock(write_lock):
        print("[Kernel] Events write lock timeout", file=sys.stderr)
        sys.exit(1)
    try:
        os.makedirs(KERNEL_DIR, exist_ok=True)
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    finally:
        _clear(write_lock)
    print(f"[Kernel] Event emitted: {type_}:{action}" + (f" -> {to}" if to else ""))


def read_events(agent, since=None):
    cursor = since if since is not None else _read_cursor(agent)
    events, lines = [], []
    if EVENTS_FILE.exists():
        lines = EVENTS_FILE.read_text(encoding="utf-8").splitlines()
    if cursor > len(lines):
        cursor = 0  # rotation happened — restart from new file
    for line in lines[cursor:]:
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
            if ev.get("to") in (None, agent):
                events.append(ev)
        except json.JSONDecodeError:
            pass
    _write_cursor(agent, len(lines))
    print(json.dumps(events))


def _read_cursor(agent):
    path = AGENTS_DIR / f"{agent}.cursor"
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return 0


def _write_cursor(agent, n):
    os.makedirs(AGENTS_DIR, exist_ok=True)
    (AGENTS_DIR / f"{agent}.cursor").write_text(str(n), encoding="utf-8")


def state_update(key, value):
    if key in PROTECTED_STATE_KEYS:
        print(f"[Kernel] Protected key: {key}", file=sys.stderr)
        sys.exit(1)
    lock = LOCKS_DIR / "state_write.lock"
    if not _spinlock(lock):
        print("[Kernel] State lock timeout", file=sys.stderr)
        sys.exit(1)
    try:
        s = _load(STATE_FILE, {})
        try:
            s[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            s[key] = value
        os.makedirs(KERNEL_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        print(f"[Kernel] State updated: {key}")
    finally:
        _clear(lock)


def state_increment(key):
    if key in PROTECTED_STATE_KEYS:
        print(f"[Kernel] Protected key: {key}", file=sys.stderr)
        sys.exit(1)
    lock = LOCKS_DIR / "state_write.lock"
    if not _spinlock(lock):
        print("[Kernel] State lock timeout", file=sys.stderr)
        sys.exit(1)
    try:
        s = _load(STATE_FILE, {})
        s[key] = int(s.get(key, 0)) + 1
        os.makedirs(KERNEL_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        print(s[key])
    finally:
        _clear(lock)


def claim_task(task_id, partition, agent, ttl=300):
    """Atomically claim a partition via directory lock. No registry — use bash wait."""
    if not _validate_agent(agent):
        sys.exit(1)
    lock = LOCKS_DIR / f"task_{task_id}_p{partition}.lock"
    os.makedirs(LOCKS_DIR, exist_ok=True)
    if lock.exists() and _is_stale(lock):
        _clear(lock)
    try:
        os.mkdir(lock)
    except FileExistsError:
        print("already_claimed")
        return
    try:
        meta = {"pid": os.getpid(), "agent": agent, "expires_at": time.time() + ttl}
        (lock / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    except OSError:
        pass
    print("claimed")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Agentic OS Kernel v3")
    s = p.add_subparsers(dest="cmd", required=True)

    a = s.add_parser("acquire_lock")
    a.add_argument("name")
    a.add_argument("--ttl", type=int, default=None)

    s.add_parser("release_lock").add_argument("name")

    e = s.add_parser("emit_event")
    e.add_argument("--agent", required=True)
    e.add_argument("--type", required=True)
    e.add_argument("--action", required=True)
    e.add_argument("--status", choices=["success", "fail"])
    e.add_argument("--summary")
    e.add_argument("--to")
    e.add_argument("--correlation-id")

    r = s.add_parser("read_events")
    r.add_argument("--agent", required=True)
    r.add_argument("--since-cursor", type=int, default=None)

    u = s.add_parser("state_update")
    u.add_argument("key")
    u.add_argument("value")

    s.add_parser("state_increment").add_argument("--key", required=True)

    c = s.add_parser("claim_task")
    c.add_argument("--task-id", required=True)
    c.add_argument("--partition", type=int, required=True)
    c.add_argument("--agent", required=True)
    c.add_argument("--ttl", type=int, default=300)

    args = p.parse_args()
    if args.cmd == "acquire_lock":       acquire_lock(args.name, args.ttl)
    elif args.cmd == "release_lock":     release_lock(args.name)
    elif args.cmd == "emit_event":       emit_event(args.agent, args.type, args.action,
                                                    args.status, args.summary,
                                                    args.to, args.correlation_id)
    elif args.cmd == "read_events":      read_events(args.agent, args.since_cursor)
    elif args.cmd == "state_update":     state_update(args.key, args.value)
    elif args.cmd == "state_increment":  state_increment(args.key)
    elif args.cmd == "claim_task":       claim_task(args.task_id, args.partition,
                                                    args.agent, args.ttl)


if __name__ == "__main__":
    main()
