#!/usr/bin/env python3
"""Deterministic launch guards and progress reconciliation (stdlib only). Owned by cli-agent; run_agent.py calls these in its launch path.

  claim / release   atomic ownership of an execution unit; a second claim FAILS before launch (prevention, not detection)
  exec-check        verify executables inside the worker's actual environment (PATH of the worker, not of the orchestrator)
  context-check     verify what context an LLM CLI call will carry, from its own stream-json init event (not self-report)
  cwd-check         working directory resolves inside the allowed root (worktree boundary)
  reconcile         progress from unique planned units: completed / malformed / duplicate / missing / unexpected
"""
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path


def claim(claim_dir, unit, owner):
    d = Path(claim_dir); d.mkdir(parents=True, exist_ok=True)
    f = _cf(d, unit)
    tmp = d / (f.name + "." + str(os.getpid()) + ".tmp")
    tmp.write_text(owner)                       # owner is written before the claim becomes visible
    try:
        os.link(tmp, f)                          # atomic: fails if the claim exists
    except FileExistsError:
        try:
            who = f.read_text().strip()
        except FileNotFoundError:
            who = "unknown (released concurrently)"
        return {"ok": False, "unit": unit, "owner": who, "why": "already owned; do not launch a duplicate"}
    finally:
        tmp.unlink()
    return {"ok": True, "unit": unit, "owner": owner}


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


def release(claim_dir, unit, owner):
    f = _cf(claim_dir, unit)
    if not f.exists():
        return {"ok": True, "released": False}
    if f.read_text().strip() != owner:
        return {"ok": False, "why": f"owned by {f.read_text().strip()}, not {owner}"}
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
    r = sub.add_parser("reconcile"); r.add_argument("planned", help="JSON list or file of ids"); r.add_argument("records", help="JSONL file"); r.add_argument("--key", default="id")
    a = ap.parse_args(argv)
    if a.cmd == "claim": out = claim(a.dir, a.unit, a.owner)
    elif a.cmd == "release": out = release(a.dir, a.unit, a.owner)
    elif a.cmd == "exec-check": out = exec_check(a.names, a.path, not a.no_version)
    elif a.cmd == "cwd-check": out = check_cwd(a.cwd, a.allowed_root)
    elif a.cmd == "context-check": out = context_check(a.stream_file, expect_cwd=a.cwd, expect_model=a.model)
    else:
        pl = json.loads(Path(a.planned).read_text()) if Path(a.planned).exists() else json.loads(a.planned)
        rows = [json.loads(l) for l in Path(a.records).read_text().splitlines() if l.strip()]
        out = reconcile(pl, rows, a.key)
    print(json.dumps(out, indent=1))
    return 0 if out.get("ok", out.get("all_valid", True)) else 1


if __name__ == "__main__":
    sys.exit(main())
