#!/usr/bin/env python3
"""Generic work-item loop driver (stdlib only): contract -> lessons -> guarded dispatch -> evaluation -> repair/accept -> lesson.

It owns sequencing and the action trace; it delegates execution to cli-agent (`run_agent.py`) and assessment to
evaluating-agent-outcomes. It requires no Sanctuary schema. State lives under <root>/.agent-work/<work-id>/ (explicit root).
Instructions an agent must follow vs controls enforced by code are listed in references/learning-loop.md.
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[1]          # .../skills (source layout and installed layout both keep skills side by side)


def _skill(name):
    cands = [SKILLS / name, Path.home() / ".claude/skills" / name, Path.home() / ".agents/skills" / name]
    for c in cands:
        if c.is_dir():
            return c
    raise SystemExit(f"required sibling skill not installed: {name}")


def _import(skill, module):
    d = str(_skill(skill) / "scripts")
    if d not in sys.path:
        sys.path.insert(0, d)
    return __import__(module)


_SAFE = __import__("re").compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _safe(name, what):
    if not _SAFE.match(name or "") or ".." in name:
        raise ValueError(f"unsafe {what} {name!r}: use letters, digits, '.', '_', '-'")
    return name


def _dir(root, wid):
    d = Path(root).resolve() / ".agent-work" / _safe(wid, "work id")
    d.mkdir(parents=True, exist_ok=True)
    return d


def trace(root, wid, action, **detail):
    rec = {"t": round(time.time(), 3), "action": action, **detail}
    with (_dir(root, wid) / "trace.jsonl").open("a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def read_trace(root, wid):
    p = _dir(root, wid) / "trace.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def start(contract_path, root=".", store=None):
    """Validate the contract, retrieve relevant lessons BEFORE any dispatch, record the plan."""
    oe, lessons = _import("evaluating-agent-outcomes", "outcome_eval"), _import("evaluating-agent-outcomes", "lessons")
    c = json.loads(Path(contract_path).read_text())
    problems = oe.validate_contract(c)
    wid = c.get("id", "unnamed")
    if problems:
        trace(root, wid, "contract_rejected", problems=problems)
        return {"ok": False, "problems": problems}
    query = " ".join([c["goal"], c["type"], " ".join(c["scope"]["paths"]), " ".join(a.get("text", "") for a in c["acceptance"])])
    found = lessons.find(query, 3, root, store)
    trace(root, wid, "lessons_retrieved", query_terms=len(query.split()), lesson_ids=[l["id"] for l in found])
    (_dir(root, wid) / "contract.json").write_text(json.dumps(c, indent=1))
    plan = {"work_id": wid, "lessons": found, "budget": c["budget"], "authorization": c["authorization"]}
    (_dir(root, wid) / "plan.json").write_text(json.dumps(plan, indent=1))
    trace(root, wid, "plan_recorded", budget=c["budget"])
    return {"ok": True, "plan": plan}


def dispatch(wid, unit, owner, cli, worker_path, instruction, cwd, root=".", executable=None, timeout=600, extra=()):
    """Guarded launch through cli-agent: preflight in the worker's PATH, then run_agent with claim/cwd/result controls."""
    guard = _import("cli-agent", "dispatch_guard")
    _safe(unit, "unit")
    exe = executable or cli
    pre = guard.exec_check([exe] if executable is None else [executable], path=worker_path if executable is None else os.environ["PATH"])
    trace(root, wid, "exec_check", ok=pre["ok"], detail=pre["results"][0]["detail"], unit=unit)
    d = _dir(root, wid)
    result = d / f"result-{unit}.json"
    result.unlink(missing_ok=True)       # never trust a result from an earlier attempt
    if not pre["ok"]:
        result.write_text(json.dumps({"schema": 1, "status": "refused", "error": "executable unavailable in worker environment", "checks": [{"name": "exec_check", **pre["results"][0]}], "usage": {"total_tokens": None, "source": "not run"}}))
        trace(root, wid, "dispatch_refused", unit=unit, reason="executable unavailable")
        return {"ok": False, "result": str(result), "status": "refused"}
    src, out = d / f"input-{unit}.md", d / f"output-{unit}.md"
    src.write_text(instruction)
    cmd = [sys.executable, str(_skill("cli-agent") / "scripts" / "run_agent.py"), "/dev/null", str(src), str(out), instruction[:200],
           "--cli", cli, "--cwd", str(cwd), "--allowed-root", str(Path(root).resolve()), "--claim-dir", str(d / "claims"), "--unit", unit,
           "--owner", owner, "--timeout", str(timeout), "--result-json", str(result), *extra]
    if executable:
        cmd += ["--executable", executable]
    env = dict(os.environ, PATH=worker_path)
    p = subprocess.run(cmd, env=env, capture_output=True, text=True)
    res = json.loads(result.read_text()) if result.exists() else {"status": "failed", "error": "no result written", "usage": {"total_tokens": None}}
    if p.returncode != 0 and res.get("status") == "ok":
        res["status"] = "failed"
    trace(root, wid, "dispatch", unit=unit, status=res["status"], exit=p.returncode, usage=res.get("usage"))
    return {"ok": res["status"] == "ok", "result": str(result), "status": res["status"]}


def evaluate(wid, root=".", manual=None, scores=None):
    """Assess the delivery; dispatch usage is summed as a LOWER BOUND when any result is unknown."""
    oe = _import("evaluating-agent-outcomes", "outcome_eval")
    d = _dir(root, wid)
    c = json.loads((d / "contract.json").read_text())
    tr = read_trace(root, wid)
    attempts = sum(1 for t in tr if t["action"] == "dispatch")
    known, unknown = 0, 0
    for r in d.glob("result-*.json"):
        u = json.loads(r.read_text()).get("usage", {}).get("total_tokens")
        known, unknown = (known + u, unknown) if u is not None else (known, unknown + 1)
    usage = {"total_tokens": known if (unknown == 0 and attempts) else None, "source": "run_agent result files"}
    lims = [f"{unknown} dispatch result(s) reported no usage"] if unknown else []
    out = oe.assess(c, root, {"manual_confirmations": manual, "scores": scores, "usage": usage, "limitations": lims}, attempts_used=attempts)
    (d / "findings.json").write_text(json.dumps(out, indent=1))
    trace(root, wid, "evaluated", complete=out["complete"], recommended=out["recommended"], incomplete=out["incomplete"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="."); ap.add_argument("--store")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("contract")
    e = sub.add_parser("evaluate"); e.add_argument("work_id")
    t = sub.add_parser("trace"); t.add_argument("work_id")
    ns = ap.parse_args(argv)
    if ns.cmd == "start": out = start(ns.contract, ns.root, ns.store)
    elif ns.cmd == "evaluate": out = evaluate(ns.work_id, ns.root)
    else: out = read_trace(ns.root, ns.work_id)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
