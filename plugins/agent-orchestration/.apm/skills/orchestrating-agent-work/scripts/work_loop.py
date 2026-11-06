#!/usr/bin/env python3
"""Single-work-item loop with immutable attempts, atomic budget admission, claim-before-artifacts and lesson application (stdlib only).

Supported entry point:  work_loop.py run CONTRACT --cli claude --model M --instruction-file TASK.md   (or work_loop.run_item(...))

What the CODE does (enforced): validate the contract and budget; retrieve lessons; for each attempt - acquire the unit claim FIRST,
admit the launch under a file lock (attempt and token budget, incomplete-usage policy), allocate an immutable attempt id and
directory, put a bounded lessons block into the worker brief, run the executor (cli-agent `run_agent.py`) with the pre-acquired claim
token, record every backend attempt and its usage, assess, and hand incomplete work back for a bounded repair until acceptance, a
concrete blocker, escalation or budget exhaustion.  What stays AGENT-SUPERVISED: authoring lessons (candidates are returned),
confirming manual criteria, judging lesson usefulness (observe_lessons needs evidence), reviews, integration and any use of
authorization.  This is a sequential single-item loop on top of run_agent.py; it is NOT a scheduler and does not replace graph_runner.py
(DAG manifests) or swarm_run.py (bulk jobs), which do not call cli-agent.

Layout under <root>/.agent-work/<work-id>/ : contract.json, plan.json, trace.jsonl, attempts.jsonl (append-only ledger),
attempts/<attempt-id>/{input.md,output.md,result.json}, evaluations/<eval-id>.json, findings.json, accepted.json, refusals.jsonl,
claims/, ledger.lock.  Protection boundary: ownership claims stop a second CLAIMANT of the same unit; they cannot stop an unrelated
process from writing these files, and a hard-killed holder leaves a stale claim (no automatic expiry).
"""
import argparse, json, os, re, subprocess, sys, time, uuid
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:                # non-POSIX: fall back to an exclusive-create lock file
    fcntl = None

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[1]          # .../skills (source layout and installed layout both keep skills side by side)
_SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
LESSON_OUTCOMES = ("helped", "no_effect", "harmful", "not_applicable")


def _skill(name):
    for c in (SKILLS / name, Path.home() / ".claude/skills" / name, Path.home() / ".agents/skills" / name):
        if c.is_dir():
            return c
    raise SystemExit(f"required sibling skill not installed: {name}")


def _import(skill, module):
    d = str(_skill(skill) / "scripts")
    if d not in sys.path:
        sys.path.insert(0, d)
    return __import__(module)


def _safe(name, what):
    if not _SAFE.match(name or "") or ".." in name:
        raise ValueError(f"unsafe {what} {name!r}: use letters, digits, '.', '_', '-'")
    return name


def _dir(root, wid):
    d = Path(root).resolve() / ".agent-work" / _safe(wid, "work id")
    d.mkdir(parents=True, exist_ok=True)
    return d


@contextmanager
def _locked(d):
    """Exclusive lock for ledger read-modify-write (admission + reservation must be atomic across concurrent dispatchers)."""
    path = Path(d) / "ledger.lock"
    if fcntl:
        with open(path, "a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    else:                                                  # pragma: no cover - exclusive-create spin lock
        while True:
            try:
                fd = os.open(path.with_suffix(".x"), os.O_CREAT | os.O_EXCL); os.close(fd); break
            except FileExistsError:
                time.sleep(0.05)
        try:
            yield
        finally:
            os.unlink(path.with_suffix(".x"))


def _append(path, rec):
    with open(path, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
        f.flush(); os.fsync(f.fileno())


def _read_jsonl(path):
    p = Path(path)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def trace(root, wid, action, **detail):
    rec = {"t": round(time.time(), 3), "action": action, **detail}
    _append(_dir(root, wid) / "trace.jsonl", rec)
    return rec


def read_trace(root, wid):
    return _read_jsonl(_dir(root, wid) / "trace.jsonl")


def _ledger(root, wid):
    d = _dir(root, wid)
    recs = _read_jsonl(d / "attempts.jsonl")
    known = {r.get("attempt_id") for r in recs if r.get("kind") == "attempt"}
    for lf in sorted(d.glob("result-*.json")):                 # compatibility: pre-hardening result files (one pseudo-attempt each)
        aid = "legacy-" + lf.stem[len("result-"):]
        if aid in known:
            continue
        try:
            r = json.loads(lf.read_text())
        except ValueError:
            continue
        recs.append({"kind": "attempt", "attempt_id": aid, "unit": lf.stem[len("result-"):], "state": "finished" if r.get("status") != "refused" else "refused_preflight",
                     "backend_attempts": [{"backend": r.get("backend"), "status": r.get("status"), "usage": r.get("usage") or {"total_tokens": None}}], "legacy": True})
    return recs


def start(contract_path, root=".", store=None):
    """Validate the contract (including budget semantics), retrieve lessons BEFORE any dispatch, record the plan."""
    oe, lessons = _import("evaluating-agent-outcomes", "outcome_eval"), _import("evaluating-agent-outcomes", "lessons")
    c = json.loads(Path(contract_path).read_text())
    wid = c.get("id", "unnamed")
    problems = oe.validate_contract(c)
    if problems:
        trace(root, wid, "contract_rejected", problems=problems)
        return {"ok": False, "problems": problems}
    query = " ".join([c["goal"], c["type"], " ".join(c["scope"]["paths"]), " ".join(a.get("text", "") for a in c["acceptance"])])
    found = lessons.find(query, 3, root, store)
    trace(root, wid, "lessons_retrieved", lesson_ids=[l["id"] for l in found])
    d = _dir(root, wid)
    (d / "contract.json").write_text(json.dumps(c, indent=1))
    plan = {"work_id": wid, "lessons": found, "budget": c["budget"], "authorization": c["authorization"], "isolation": c.get("isolation")}
    (d / "plan.json").write_text(json.dumps(plan, indent=1))
    trace(root, wid, "plan_recorded", budget=c["budget"])
    return {"ok": True, "plan": plan}


def _next_attempt_id(recs, unit):
    n = max([int(m.group(1)) for r in recs if r.get("kind") == "attempt" and r.get("unit") == unit
             for m in [re.search(r"-a(\d+)$", r.get("attempt_id", ""))] if m] or [0]) + 1
    return f"{unit}-a{n:03d}"


def _enc_project(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(Path(path).resolve()))


def _attribute_claude(bas, res, projects_dir=None):
    """Fill UNKNOWN usage of a claude backend attempt from Claude's own transcripts (existing supported source:
    usage_measure.claude_tokens_between) - no new tracker and no prompt sent. Attributed only when the worker's exact cwd has a transcript
    directory with activity in the attempt window and NO other session was active there; otherwise usage stays unknown.
    total_tokens = input + output + cache-write tokens (cache READS are reported but excluded from the budgeted total)."""
    um = _import("evaluating-agent-outcomes", "usage_measure")
    from datetime import datetime, timezone
    iso = lambda t: datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pd = Path(projects_dir) if projects_dir else Path.home() / ".claude" / "projects"
    out = []
    for ba in bas:
        u = ba.get("usage") or {}
        if ba.get("backend") != "claude" or u.get("total_tokens") is not None or not res.get("cwd") or not ba.get("started") or not ba.get("ended"):
            out.append(ba); continue
        d = pd / _enc_project(res["cwd"])
        if not d.is_dir():
            out.append({**ba, "usage": {**u, "source": "no claude transcript directory for the worker cwd; unknown"}}); continue
        m = um.claude_tokens_between(d, iso(ba["started"] - 1), iso(ba["ended"] + 1))
        total = m["input_tokens"] + m["output_tokens"] + m["cache_creation_input_tokens"]
        if m["concurrent"] or total == 0:
            why = "concurrent sessions in the window; not attributed" if m["concurrent"] else "no transcript usage in the attempt window"
            out.append({**ba, "usage": {"total_tokens": None, "source": "claude transcripts: " + why, "window_components": m}}); continue
        out.append({**ba, "usage": {"total_tokens": total, "tokens_in": m["input_tokens"], "tokens_out": m["output_tokens"],
                                    "cache_write": m["cache_creation_input_tokens"], "cache_read": m["cache_read_input_tokens"],
                                    "source": "claude project transcript (exact worker cwd, attempt window)",
                                    "counts": "input+output+cache_write; cache reads excluded"}})
    return out


def dispatch(wid, unit, owner, cli, worker_path, instruction, cwd, root=".", executable=None, model=None, timeout=600, extra=(), lessons_supplied=None):
    """One guarded execution attempt. ORDER matters: claim -> admit+reserve (locked) -> artifacts -> preflights -> executor -> record -> release.
    A refused duplicate or a budget refusal creates/changes NO attempt files."""
    guard, acct, lesson_mod = _import("cli-agent", "dispatch_guard"), _import("evaluating-agent-outcomes", "accounting"), _import("evaluating-agent-outcomes", "lessons")
    _safe(unit, "unit")
    d = _dir(root, wid)
    contract = json.loads((d / "contract.json").read_text())
    claims = d / "claims"
    c = guard.claim(claims, unit, owner)                         # 1. ownership BEFORE touching execution-specific state
    if not c["ok"]:
        _append(d / "refusals.jsonl", {"t": time.time(), "unit": unit, "owner": owner, "reason": "duplicate", "held_by": c["owner"]})
        trace(root, wid, "dispatch_refused", unit=unit, reason="duplicate", held_by=c["owner"])
        return {"ok": False, "status": "duplicate", "reason": f"unit {unit} is owned by {c['owner']}"}
    token = c["token"]
    try:
        with _locked(d):                                         # 2. atomic admission + reservation
            recs = _ledger(root, wid)
            decision = acct.admit(contract["budget"], acct.summarize_attempts(recs))
            if not decision["ok"]:
                _append(d / "refusals.jsonl", {"t": time.time(), "unit": unit, "reason": "budget", "detail": decision["reason"]})
                trace(root, wid, "dispatch_refused", unit=unit, reason="budget", detail=decision["reason"])
                return {"ok": False, "status": "budget_exhausted", "reason": decision["reason"]}
            attempt_id = _next_attempt_id(recs, unit)
            _append(d / "attempts.jsonl", {"kind": "attempt", "attempt_id": attempt_id, "unit": unit, "work_id": wid, "state": "reserved", "owner": owner,
                                           "reserve_tokens": decision["reserve_tokens"], "backend": cli, "model": model, "t": time.time()})
        try:
            adir = d / "attempts" / attempt_id
            adir.mkdir(parents=True, exist_ok=False)                  # immutable identity: never reused
            lesson_text, ids = lesson_mod.brief_section(lessons_supplied or [])
            brief = instruction + ("\n\n" + lesson_text if lesson_text else "")
            (adir / "input.md").write_text(brief)
            result = adir / "result.json"
            _append(d / "attempts.jsonl", {"kind": "attempt", "attempt_id": attempt_id, "unit": unit, "work_id": wid, "state": "reserved", "owner": owner,
                                           "reserve_tokens": decision["reserve_tokens"], "backend": cli, "model": model, "lessons_supplied": ids, "t": time.time()})
            trace(root, wid, "attempt_reserved", unit=unit, attempt_id=attempt_id, lessons_supplied=ids)

            def refuse(reason, detail):
                result.write_text(json.dumps({"schema": 1, "status": "refused", "error": reason, "checks": [detail], "usage": {"total_tokens": None, "source": "not run"}}))
                _append(d / "attempts.jsonl", {"kind": "attempt", "attempt_id": attempt_id, "unit": unit, "work_id": wid, "state": "refused_preflight", "reason": reason, "t": time.time()})
                trace(root, wid, "dispatch_refused", unit=unit, attempt_id=attempt_id, reason=reason)
                return {"ok": False, "status": "refused", "attempt_id": attempt_id, "result": str(result), "reason": reason}

            if contract.get("isolation", {}).get("required"):         # experimental readiness: configuration-level probe must exist for THIS config
                rs = guard.readiness_status({"cli": cli, "model": model, "executable": executable or cli, "search_path": worker_path,
                                             "flags": guard.CLEAN_FLAGS + list(extra)}, d.parent / "readiness")
                trace(root, wid, "readiness_checked", attempt_id=attempt_id, ready=rs["ready"], fingerprint=rs["fingerprint"][:12])
                if not rs["ready"]:
                    return refuse("isolation required but not verified: " + rs["reason"], {"name": "readiness", "ok": False, **rs})
            pre = guard.exec_check([executable] if executable else [cli], path=os.environ["PATH"] if executable else worker_path)
            trace(root, wid, "exec_check", ok=pre["ok"], detail=pre["results"][0]["detail"], unit=unit, attempt_id=attempt_id)
            if not pre["ok"]:
                return refuse("executable unavailable in worker environment", {"name": "exec_check", **pre["results"][0]})
            cmd = [sys.executable, str(_skill("cli-agent") / "scripts" / "run_agent.py"), "/dev/null", str(adir / "input.md"), str(adir / "output.md"), brief[:200],
                   "--cli", cli, "--claim-dir", str(claims), "--unit", unit, "--owner", owner,
                   "--claim-token", token, "--timeout", str(timeout), "--result-json", str(result), *extra]
            if not contract.get("isolation", {}).get("required"):     # isolated experimental calls run in the executor's neutral cwd instead
                cmd += ["--cwd", str(cwd), "--allowed-root", str(Path(root).resolve())]
            if model:
                cmd += ["--model", model]
            if executable:
                cmd += ["--executable", executable]
            if contract.get("isolation", {}).get("required"):
                cmd += ["--clean-context"]
            p = subprocess.run(cmd, env=dict(os.environ, PATH=worker_path), capture_output=True, text=True)
            res = json.loads(result.read_text()) if result.exists() else {"status": "failed", "error": "no result written", "attempts": [], "usage": {"total_tokens": None}}
            if p.returncode != 0 and res.get("status") == "ok":
                res["status"] = "failed"
            if res.get("status") == "refused":                       # the executor refused before launching anything: not an execution attempt
                _append(d / "attempts.jsonl", {"kind": "attempt", "attempt_id": attempt_id, "unit": unit, "work_id": wid, "state": "refused_preflight",
                                               "reason": res.get("error") or "executor refused", "t": time.time()})
                trace(root, wid, "dispatch_refused", unit=unit, attempt_id=attempt_id, reason=res.get("error"))
                return {"ok": False, "status": "refused", "attempt_id": attempt_id, "result": str(result), "reason": res.get("error")}
            bas = res.get("attempts") or [{"backend": cli, "status": res.get("status"), "usage": res.get("usage") or {"total_tokens": None}}]
            bas = _attribute_claude(bas, res)
            _append(d / "attempts.jsonl", {"kind": "attempt", "attempt_id": attempt_id, "unit": unit, "work_id": wid, "state": "finished", "status": res.get("status"),
                                           "backend_attempts": bas, "cleanup_confirmed": res.get("cleanup_confirmed"), "lessons_supplied": ids, "t": time.time()})
            trace(root, wid, "dispatch", unit=unit, attempt_id=attempt_id, status=res.get("status"), exit=p.returncode, backend_attempts=len(bas))
            return {"ok": res.get("status") == "ok", "status": res.get("status"), "attempt_id": attempt_id, "result": str(result), "lessons_supplied": ids}
        except Exception as exc:                                  # noqa: BLE001 - a crash after reservation must not leak a reserved attempt
            _append(d / "attempts.jsonl", {"kind": "attempt", "attempt_id": attempt_id, "unit": unit, "work_id": wid, "state": "finished", "status": "failed",
                                           "error": f"{type(exc).__name__}: {exc}", "backend_attempts": [{"backend": cli, "status": "failed", "usage": {"total_tokens": None, "source": "attempt crashed"}}], "t": time.time()})
            trace(root, wid, "dispatch_crashed", unit=unit, attempt_id=attempt_id, error=f"{type(exc).__name__}: {exc}")
            return {"ok": False, "status": "failed", "attempt_id": attempt_id, "reason": f"{type(exc).__name__}: {exc}"}
    finally:
        guard.release(claims, unit, token=token)                  # only the claim THIS invocation acquired; after executor cleanup


def evaluate(wid, root=".", manual=None, scores=None):
    """Assess the work. Execution cost = every backend attempt of every attempt (failed, retried, fallback), counted once, with unknown
    usage kept unknown (known totals are lower bounds). The evaluation itself is deterministic: recorded as an evaluation call with 0 model tokens."""
    oe, acct = _import("evaluating-agent-outcomes", "outcome_eval"), _import("evaluating-agent-outcomes", "accounting")
    d = _dir(root, wid)
    c = json.loads((d / "contract.json").read_text())
    summ = acct.summarize_attempts(_ledger(root, wid))
    lims = []
    if summ["execution_tokens_is_lower_bound"]:
        lims.append(f"execution usage incomplete: {summ['backend_attempts_with_unknown_usage']} backend attempt(s) unknown, "
                    f"{summ['running_or_unfinished']} unfinished; known tokens are a lower bound")
    usage_tokens = summ["execution_tokens_known"] if (summ["backend_attempts"] and (summ["execution_tokens_known"] > 0 or not summ["execution_tokens_is_lower_bound"])) else None
    out = oe.assess(c, root, {"manual_confirmations": manual, "scores": scores, "limitations": lims,
                              "usage": {"total_tokens": usage_tokens, "source": "attempt ledger (sum of backend attempts)", "lower_bound": summ["execution_tokens_is_lower_bound"]}},
                    attempts_used=summ["execution_attempts"])
    out["accounting"] = summ
    eval_id = f"eval-{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"
    (d / "evaluations").mkdir(exist_ok=True)
    (d / "evaluations" / f"{eval_id}.json").write_text(json.dumps(out, indent=1))        # history is kept; findings.json is only the latest
    (d / "findings.json").write_text(json.dumps(out, indent=1))
    _append(d / "attempts.jsonl", {"kind": "evaluation", "eval_id": eval_id, "work_id": wid, "model_tokens": 0, "calls_model": False, "t": time.time()})
    if out["complete"]:
        fin = [r for r in _ledger(root, wid) if r.get("kind") == "attempt" and r.get("state") == "finished" and r.get("status") == "ok"]
        (d / "accepted.json").write_text(json.dumps({"eval_id": eval_id, "accepted_attempt_id": fin[-1]["attempt_id"] if fin else None,
                                                     "note": "latest successfully finished attempt at the time the criteria passed"}, indent=1))
    trace(root, wid, "evaluated", eval_id=eval_id, complete=out["complete"], recommended=out["recommended"], incomplete=out["incomplete"])
    return out


def observe_lessons(wid, outcomes, evidence_attempts, root=".", store=None):
    """Record lesson usefulness ONLY from observed execution evidence: the lesson must have been supplied to an attempt of this work item,
    and the caller must cite existing attempt ids that show the effect. Retrieval alone never marks a lesson helped."""
    lessons = _import("evaluating-agent-outcomes", "lessons")
    recs = _ledger(root, wid)
    ids = {r["attempt_id"] for r in recs if r.get("kind") == "attempt"}
    supplied = {l for r in recs if r.get("kind") == "attempt" for l in (r.get("lessons_supplied") or [])}
    if not evidence_attempts or not set(evidence_attempts) <= ids:
        raise ValueError("evidence_attempts must name existing attempt ids of this work item")
    final = {}
    for r in recs:
        if r.get("kind") == "attempt":
            final[r["attempt_id"]] = r                                # last record per attempt wins
    not_run = [a for a in evidence_attempts if final[a].get("state") != "finished"]
    if not_run:
        raise ValueError(f"evidence attempts never executed to completion (state != finished): {not_run}")
    done = []
    for lid, outcome in outcomes.items():
        if outcome not in LESSON_OUTCOMES:
            raise ValueError(f"outcome must be one of {LESSON_OUTCOMES}")
        if lid not in supplied:
            raise ValueError(f"lesson {lid} was never supplied to an attempt of {wid}")
        if not any(lid in (final[a].get("lessons_supplied") or []) for a in evidence_attempts):
            raise ValueError(f"lesson {lid} was not supplied to any of the cited evidence attempts {list(evidence_attempts)}; cite the attempt(s) that carried it")
        done.append(lessons.use(lid, f"{wid}:{','.join(evidence_attempts)}", outcome, root, store))
    trace(root, wid, "lessons_observed", outcomes=outcomes, evidence_attempts=list(evidence_attempts))
    return done


def run_item(contract_path, root, cli, instruction, cwd=None, worker_path=None, executable=None, model=None, timeout=600, extra=(), unit=None, owner="work_loop", store=None):
    """The supported normal path: contract -> lessons -> bounded repair loop -> stop on acceptance / blocker / escalation / budget."""
    st = start(contract_path, root, store)
    if not st["ok"]:
        return {"ok": False, "stopped": "contract_invalid", "problems": st["problems"]}
    wid, plan = st["plan"]["work_id"], st["plan"]
    acct = _import("evaluating-agent-outcomes", "accounting")
    unit = unit or "u1"
    brief, last, history = instruction, None, []
    for _ in range(plan["budget"]["max_attempts"] + 1):                    # +1 so the budget gate (not the loop bound) is what stops us
        r = dispatch(wid, unit, owner, cli, worker_path or os.environ["PATH"], brief, cwd or root, root, executable, model, timeout, extra, plan["lessons"])
        history.append({k: r.get(k) for k in ("status", "attempt_id", "reason")})
        if r["status"] in ("duplicate", "budget_exhausted", "refused"):
            stop = {"duplicate": "blocked_duplicate", "budget_exhausted": "budget_exhausted", "refused": "blocked_preflight"}[r["status"]]
            return {"ok": False, "stopped": stop, "reason": r.get("reason"), "attempts": history, "findings": last, "lesson_candidates": _candidates(root, wid)}
        last = evaluate(wid, root)
        if last["complete"]:
            return {"ok": True, "stopped": "accepted", "attempts": history, "findings": last, "lesson_candidates": _candidates(root, wid),
                    "integration_allowed": last["integration_allowed"]}
        if last["recommended"] in ("blocked", "escalate", "fix_contract"):
            return {"ok": False, "stopped": last["recommended"], "attempts": history, "findings": last, "lesson_candidates": _candidates(root, wid)}
        brief = instruction + "\n\n## Repair required (previous attempt left these unmet)\n" + "\n".join(f"- {x}" for x in last["repair_instructions"])
    return {"ok": False, "stopped": "loop_bound", "attempts": history, "findings": last}


def _candidates(root, wid):
    """Suggestions for the agent to turn into lessons: a failed/refused/timed-out attempt later followed by a finished ok attempt. NOT recorded."""
    recs = [r for r in _ledger(root, wid) if r.get("kind") == "attempt" and r.get("state") in ("finished", "refused_preflight")]
    out = []
    for i, r in enumerate(recs):
        bad = r.get("state") == "refused_preflight" or r.get("status") in ("failed", "timeout")
        if bad and any(x.get("status") == "ok" for x in recs[i + 1:]):
            out.append({"failed_attempt": r["attempt_id"], "failure": r.get("reason") or r.get("status"), "repaired_by": next(x["attempt_id"] for x in recs[i + 1:] if x.get("status") == "ok")})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="."); ap.add_argument("--store")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("contract"); r.add_argument("--cli", required=True); r.add_argument("--model"); r.add_argument("--executable")
    r.add_argument("--worker-path"); r.add_argument("--instruction-file", required=True); r.add_argument("--cwd"); r.add_argument("--timeout", type=float, default=600)
    r.add_argument("--unit", default="u1"); r.add_argument("--owner", default="work_loop")
    s = sub.add_parser("start"); s.add_argument("contract")
    e = sub.add_parser("evaluate"); e.add_argument("work_id")
    t = sub.add_parser("trace"); t.add_argument("work_id")
    ns = ap.parse_args(argv)
    if ns.cmd == "run":
        out = run_item(ns.contract, ns.root, ns.cli, Path(ns.instruction_file).read_text(), ns.cwd, ns.worker_path, ns.executable, ns.model, ns.timeout,
                       unit=ns.unit, owner=ns.owner, store=ns.store)
    elif ns.cmd == "start": out = start(ns.contract, ns.root, ns.store)
    elif ns.cmd == "evaluate": out = evaluate(ns.work_id, ns.root)
    else: out = read_trace(ns.root, ns.work_id)
    print(json.dumps(out, indent=1))
    return 0 if (out.get("ok", True) if isinstance(out, dict) else True) else 1


if __name__ == "__main__":
    sys.exit(main())
