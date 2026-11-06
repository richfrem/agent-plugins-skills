#!/usr/bin/env python3
"""Deterministic launch guards and progress reconciliation (stdlib only). Owned by cli-agent; run_agent.py calls these in its launch path.

  claim / release   atomic ownership of an execution unit; a second claim FAILS before launch (prevention, not detection)
  exec-check        verify executables inside the worker's actual environment (PATH of the worker, not of the orchestrator)
  context-check     verify what context an LLM CLI call will carry, from its own stream-json init event (not self-report)
  cwd-check         working directory resolves inside the allowed root (worktree boundary)
  probe-context     ONE configuration-level clean-context probe (stream-json); readiness  checks a probe exists for this exact config
  reconcile         progress from unique planned units: completed / malformed / duplicate / missing / unexpected
"""
import argparse, hashlib, json, os, shutil, signal, subprocess, sys, time, uuid
from pathlib import Path


def _read_claim(f):
    """Claim file content -> dict. Legacy files held a bare owner string; they have no token."""
    try:
        raw = f.read_text().strip()
    except FileNotFoundError:
        return None
    try:
        d = json.loads(raw)
        if isinstance(d, dict):
            return d
    except ValueError:
        pass
    return {"owner": raw, "token": None, "legacy": True}


def claim(claim_dir, unit, owner):
    """Atomically claim a unit. The claim carries a unique token (generation); only the holder of that token may release it.
    Protection boundary: this stops a second CLAIMANT using the same claim directory. It cannot stop an unrelated process from
    writing the same files, and a hard-killed holder leaves a stale claim (no automatic expiry)."""
    d = Path(claim_dir); d.mkdir(parents=True, exist_ok=True)
    f = _cf(d, unit)
    token = uuid.uuid4().hex
    tmp = d / (f.name + "." + token[:8] + ".tmp")
    tmp.write_text(json.dumps({"owner": owner, "token": token, "pid": os.getpid(), "unit": unit}))   # complete before visible
    try:
        try:
            os.link(tmp, f)                      # atomic and complete-before-visible: fails if the claim exists
        except FileExistsError:
            cur = _read_claim(f) or {}
            return {"ok": False, "unit": unit, "owner": cur.get("owner", "unknown (released concurrently)"),
                    "why": "already owned; do not launch a duplicate"}
        except OSError:                          # filesystem without hard links: exclusive create (a reader may briefly see an empty file)
            try:
                fd = os.open(f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                cur = _read_claim(f) or {}
                return {"ok": False, "unit": unit, "owner": cur.get("owner", "unknown (released concurrently)"),
                        "why": "already owned; do not launch a duplicate"}
            with os.fdopen(fd, "w") as h:
                h.write(tmp.read_text())
    finally:
        tmp.unlink()
    return {"ok": True, "unit": unit, "owner": owner, "token": token}


def verify_claim(claim_dir, unit, token):
    """True only if the claim exists and carries exactly this token (used by an executor handed a pre-acquired claim)."""
    cur = _read_claim(_cf(claim_dir, unit))
    return bool(cur and token and cur.get("token") == token)


def check_cwd(cwd, allowed_root):
    """The working directory must exist and resolve (symlinks followed) inside allowed_root."""
    c, r = Path(cwd).resolve(), Path(allowed_root).resolve()
    if not c.is_dir():
        return {"ok": False, "detail": f"cwd {cwd} is not a directory"}
    if c != r and r not in c.parents:
        return {"ok": False, "detail": f"cwd {c} escapes allowed root {r}"}
    return {"ok": True, "detail": str(c)}


def _cf(d, unit):
    return Path(d) / (hashlib.sha256(unit.encode()).hexdigest()[:16] + ".owner")


def release(claim_dir, unit, owner=None, token=None):
    """Release only the claim this invocation acquired. With a token the token must match; without one (legacy callers) the owner must."""
    f = _cf(claim_dir, unit)
    cur = _read_claim(f)
    if cur is None:
        return {"ok": True, "released": False}
    if token is not None:
        if cur.get("token") != token:
            return {"ok": False, "why": "claim token mismatch: not the holder"}
    elif cur.get("owner") != owner:
        return {"ok": False, "why": f"owned by {cur.get('owner')}, not {owner}"}
    f.unlink()
    return {"ok": True, "released": True}


def exec_check(names, path, run_version=True):
    """Resolve each executable on the WORKER's `path` (required: the orchestrator's PATH proves nothing) and run `<exe> --version` under it.
    Pass path=os.environ["PATH"] only when this process IS the worker (run it from the worker's wrapper)."""
    if not path:
        raise ValueError("path is required: check the worker's PATH, not the orchestrator's")
    env = dict(os.environ)
    env["PATH"] = path
    results = []
    for n in names:
        exe = shutil.which(n, path=env.get("PATH"))
        ok, detail = bool(exe), "not found on PATH" if not exe else exe
        if exe and run_version:
            try:
                p = subprocess.run([exe, "--version"], env=env, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
                ok = p.returncode == 0
                detail = exe if ok else f"{exe} --version exited {p.returncode}"
            except Exception as e:  # noqa: BLE001
                ok, detail = False, f"{exe}: {e}"
        results.append({"name": n, "ok": ok, "detail": detail})
    return {"ok": all(r["ok"] for r in results), "results": results}


def context_problems(init, hook_events=0, expect_cwd=None, expect_model=None, forbid_repo_markers=("CLAUDE.md", "AGENTS.md")):
    """Problems in a claude stream-json `init` event that would contaminate an experiment. Empty list = clean as observable.

    Anything the CLI does not report (e.g. server-side defaults) remains unobserved: callers must record that.
    """
    problems = []
    if hook_events:
        problems.append(f"{hook_events} hook events")
    for key, label in (("slash_commands", "slash commands"), ("skills", "skills"), ("tools", "tools"), ("mcp_servers", "mcp servers"), ("agents", "agents")):
        if init.get(key):
            problems.append(f"{label} loaded")
    if init.get("plugins"):
        problems.append("plugins loaded")
    for req in ("cwd", "model"):
        if req not in init:
            problems.append(f"init event lacks '{req}': context unobservable")
    mem = (init.get("memory_paths") or {}).get("auto", "")
    if mem and (Path(mem) / "MEMORY.md").exists():
        problems.append(f"auto memory present at {mem}")
    cwd = init.get("cwd")
    if expect_cwd and cwd and Path(cwd).resolve() != Path(expect_cwd).resolve():
        problems.append(f"cwd {cwd} != {expect_cwd}")
    if cwd:
        for m in forbid_repo_markers:
            if (Path(cwd) / m).exists():
                problems.append(f"{m} in cwd {cwd}")
    if expect_model and init.get("model") != expect_model:
        problems.append(f"model {init.get('model')} != {expect_model}")
    return problems


def context_check(stream_file, **kw):
    events = [json.loads(l) for l in Path(stream_file).read_text().splitlines() if l.strip().startswith("{")]
    inits = [e for e in events if e.get("type") == "system" and e.get("subtype") == "init"]
    if not inits:
        return {"ok": False, "problems": ["no init event: context unobservable, do not launch"]}
    init = inits[0]
    hooks = sum(1 for e in events if e.get("type") == "system" and "hook" in str(e.get("subtype")))
    pr = context_problems(init, hooks, **kw)
    for extra in inits[1:]:
        pr += ["additional init event: " + x for x in context_problems(extra, 0, **kw)] or ["additional init event (session changed mid-stream)"]
    return {"ok": not pr, "problems": pr, "unobserved": ["server-side system prompt", "model-side defaults"]}


# ---------------------------------------------------------------- process-group ownership and cleanup
def _group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def terminate_group(proc, grace=2.0, confirm_timeout=5.0):
    """Stop a worker we launched with start_new_session=True and ALL its descendants that stayed in that session/group.

    Only the group whose id equals proc.pid (the group this invocation created) is ever signalled; anything else is refused.
    Escalates SIGTERM -> SIGKILL and returns once the group is confirmed gone (or reports confirmed=False). Descendants that
    deliberately create their own session (setsid) leave the group and cannot be reached; that is a documented limit.
    On non-POSIX platforms the tree is stopped with taskkill /T (not exercised by the test-suite)."""
    if os.name != "posix":
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=10)
        except Exception:  # noqa: BLE001
            proc.kill()
        try:
            proc.wait(timeout=confirm_timeout)
        except Exception:  # noqa: BLE001
            pass
        return {"confirmed": proc.poll() is not None, "method": "taskkill /T", "platform": os.name}
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        pgid = proc.pid
    if pgid != proc.pid:
        return {"confirmed": False, "method": "refused", "detail": "worker is not the leader of its own group; not signalling"}
    for sig, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, confirm_timeout)):
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            break
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            try:
                proc.poll()                      # reap the leader so it does not look alive
            except Exception:  # noqa: BLE001
                pass
            if not _group_alive(pgid):
                break
            time.sleep(0.05)
        if not _group_alive(pgid):
            break
    try:
        proc.wait(timeout=1)
    except Exception:  # noqa: BLE001
        pass
    return {"confirmed": not _group_alive(pgid), "method": "killpg SIGTERM->SIGKILL", "pgid": pgid}


# ---------------------------------------------------------------- experimental context readiness (configuration-level)
CLEAN_FLAGS = ["--setting-sources", "project", "--disable-slash-commands", "--tools", ""]   # single source for run_agent and the probe


def config_fingerprint(cfg):
    """Stable id of everything that determines the call context: backend, model, resolved executable AND its version, flags,
    cwd policy and the env variable NAMES passed through. Any change yields a different fingerprint, so old readiness is void."""
    sp = cfg.get("search_path")          # the WORKER's PATH: the executable that will really run is the one found there
    exe = shutil.which(cfg["executable"], path=sp) if cfg.get("executable") and os.sep not in cfg["executable"] else cfg.get("executable")
    version = None
    if exe:
        try:
            p = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=15, stdin=subprocess.DEVNULL,
                               env=dict(os.environ, PATH=sp) if sp else None)
            version = p.stdout.strip() if p.returncode == 0 else f"exit {p.returncode}"
        except Exception as e:  # noqa: BLE001
            version = f"unavailable: {type(e).__name__}"
    basis = {"cli": cfg.get("cli"), "model": cfg.get("model"), "executable": os.path.realpath(exe) if exe else None, "version": version,
             "flags": list(cfg.get("flags", [])), "cwd_policy": cfg.get("cwd_policy", "neutral-temp"),
             "env_names": sorted(cfg.get("env_names", []))}
    return hashlib.sha256(json.dumps(basis, sort_keys=True).encode()).hexdigest(), basis


def probe_claude_context(cfg, readiness_dir, timeout=120):
    """ONE configuration-level probe: a single cheap stream-json call from a neutral cwd with the clean flags, judged by the CLI's own
    init/hook events via context_check (never by model self-report). Writes <readiness_dir>/<fingerprint16>.json."""
    import tempfile
    fp, basis = config_fingerprint(cfg)
    exe = basis["executable"] or cfg.get("executable") or "claude"
    work = tempfile.mkdtemp(prefix="ctx-probe-")
    cmd = [exe, "--model", cfg["model"], "-p", "Reply with exactly: OK", "--output-format", "stream-json", "--verbose", *cfg.get("flags", CLEAN_FLAGS)]
    try:
        p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        stream = Path(work) / "stream.jsonl"
        stream.write_text(p.stdout)
        res = context_check(stream, expect_cwd=work, expect_model=cfg["model"])
        rc = p.returncode
    except Exception as e:  # noqa: BLE001
        res, rc = {"ok": False, "problems": [f"probe failed: {type(e).__name__}: {e}"], "unobserved": []}, None
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rec = {"v": 1, "fingerprint": fp, "basis": basis, "ok": bool(res["ok"]), "problems": res["problems"], "unobserved": res.get("unobserved", []),
           "probe_exit": rc, "probed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "scope": "configuration-level: valid only for this exact fingerprint; one probe covers all trials that use it"}
    d = Path(readiness_dir); d.mkdir(parents=True, exist_ok=True)
    (d / (fp[:16] + ".json")).write_text(json.dumps(rec, indent=1))
    return rec


def readiness_status(cfg, readiness_dir):
    """Is there a successful probe for EXACTLY this configuration? Fingerprint mismatch (new model, flag, executable, version...) => not ready."""
    fp, _ = config_fingerprint(cfg)
    f = Path(readiness_dir) / (fp[:16] + ".json")
    if not f.is_file():
        return {"ready": False, "fingerprint": fp, "reason": "no successful context probe for this configuration"}
    rec = json.loads(f.read_text())
    if rec.get("fingerprint") != fp:
        return {"ready": False, "fingerprint": fp, "reason": "probe record does not match the current configuration"}
    if not rec.get("ok"):
        return {"ready": False, "fingerprint": fp, "reason": "probe found problems: " + "; ".join(rec.get("problems", []))}
    return {"ready": True, "fingerprint": fp, "unobserved": rec.get("unobserved", []), "probed_at": rec.get("probed_at")}


def _valid(r):
    return r.get("valid", True) is True


def reconcile(planned, records, key="id", valid=_valid):
    """planned: iterable of unit ids. records: log rows (may repeat). Report unique units, not log rows."""
    planned = list(dict.fromkeys(planned))
    seen, dup = {}, {}
    for r in records:
        k = r.get(key)
        if k is None:
            dup["<no id>"] = dup.get("<no id>", 0) + 1
            continue
        if k in seen:
            dup[k] = dup.get(k, 1) + 1
            if not valid(seen[k]) and valid(r):   # a valid retry supersedes a malformed first row
                seen[k] = r
        else:
            seen[k] = r
    completed = [k for k in planned if k in seen and valid(seen[k])]
    malformed = [k for k in planned if k in seen and not valid(seen[k])]
    missing = [k for k in planned if k not in seen]
    unexpected = sorted((k for k in seen if k not in set(planned)), key=str)
    return {"planned": len(planned), "completed": len(completed), "malformed": len(malformed), "missing": len(missing),
            "duplicates": dup, "unexpected": unexpected, "log_rows": len(records), "done": not missing and not unexpected,
            "all_valid": not missing and not unexpected and not malformed}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("claim", "release"):
        p = sub.add_parser(n); p.add_argument("--dir", required=True); p.add_argument("--unit", required=True); p.add_argument("--owner", required=True)
    e = sub.add_parser("exec-check"); e.add_argument("names", nargs="+"); e.add_argument("--path", required=True, help="the WORKER's PATH"); e.add_argument("--no-version", action="store_true")
    c = sub.add_parser("context-check"); c.add_argument("stream_file"); c.add_argument("--cwd"); c.add_argument("--model")
    w = sub.add_parser("cwd-check"); w.add_argument("cwd"); w.add_argument("--allowed-root", required=True)
    pc = sub.add_parser("probe-context"); pc.add_argument("--model", required=True); pc.add_argument("--executable", default="claude"); pc.add_argument("--readiness-dir", required=True)
    rs = sub.add_parser("readiness"); rs.add_argument("--model", required=True); rs.add_argument("--executable", default="claude"); rs.add_argument("--readiness-dir", required=True)
    r = sub.add_parser("reconcile"); r.add_argument("planned", help="JSON list or file of ids"); r.add_argument("records", help="JSONL file"); r.add_argument("--key", default="id")
    a = ap.parse_args(argv)
    if a.cmd == "claim": out = claim(a.dir, a.unit, a.owner)
    elif a.cmd == "release": out = release(a.dir, a.unit, a.owner)
    elif a.cmd == "exec-check": out = exec_check(a.names, a.path, not a.no_version)
    elif a.cmd == "cwd-check": out = check_cwd(a.cwd, a.allowed_root)
    elif a.cmd == "probe-context": out = probe_claude_context({"cli": "claude", "model": a.model, "executable": a.executable, "flags": CLEAN_FLAGS}, a.readiness_dir)
    elif a.cmd == "readiness": out = readiness_status({"cli": "claude", "model": a.model, "executable": a.executable, "flags": CLEAN_FLAGS}, a.readiness_dir)
    elif a.cmd == "context-check": out = context_check(a.stream_file, expect_cwd=a.cwd, expect_model=a.model)
    else:
        pl = json.loads(Path(a.planned).read_text()) if Path(a.planned).exists() else json.loads(a.planned)
        rows = [json.loads(l) for l in Path(a.records).read_text().splitlines() if l.strip()]
        out = reconcile(pl, rows, a.key)
    print(json.dumps(out, indent=1))
    return 0 if out.get("ok", out.get("ready", out.get("all_valid", True))) else 1


if __name__ == "__main__":
    sys.exit(main())
