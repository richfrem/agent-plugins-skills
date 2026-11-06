#!/usr/bin/env python3
"""Assess a delivery against a work contract (stdlib only). The evaluator supplies FINDINGS; the orchestrator decides.

Scores (optional rubric) never change `complete` or `integration_allowed`; successful checks never expand authorization.
Contract schema: references/work-contract.md.  CLI:  outcome_eval.py assess CONTRACT.json [--root DIR] [--evidence EV.json]
"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scoring  # noqa: E402
import accounting  # noqa: E402

CHECK_KINDS = ("command", "file_exists", "file_contains", "manual")


def validate_contract(c):
    """Returns a list of problems (empty = usable). A contract needs observable acceptance and failure conditions, scope and budget."""
    p = []
    for k in ("id", "type", "goal"):
        if not c.get(k):
            p.append(f"missing {k}")
    if not isinstance(c.get("scope"), dict) or not c["scope"].get("paths"):
        p.append("scope.paths is required (what may change)")
    acc = c.get("acceptance")
    if not acc:
        p.append("acceptance criteria are required")
    for a in acc or []:
        if not a.get("id") or not isinstance(a.get("check"), dict) or a["check"].get("kind") not in CHECK_KINDS:
            p.append(f"acceptance {a.get('id')}: needs id and check.kind in {CHECK_KINDS}")
    if not c.get("failure_conditions"):
        p.append("failure_conditions are required (state at least one)")
    p.extend(accounting.validate_budget(c.get("budget")))
    au = c.get("authorization")
    if not isinstance(au, dict):
        p.append("authorization is required (e.g. {\"may_merge\": false})")
    elif "may_merge" in au and not isinstance(au["may_merge"], bool):
        p.append("authorization.may_merge must be a boolean")
    if acc and not any(a.get("required", True) is True for a in acc if isinstance(a, dict)):
        p.append("at least one acceptance criterion must be required")
    for f in c.get("failure_conditions") or []:
        if not isinstance(f, dict) or not f.get("id") or not isinstance(f.get("check"), dict) or f["check"].get("kind") not in CHECK_KINDS:
            p.append(f"failure condition {f.get('id') if isinstance(f, dict) else f}: needs id and an evaluable check (kind in {CHECK_KINDS})")
    return p


def _inside(root, path):
    r, q = Path(root).resolve(), (Path(root) / path).resolve()
    return q == r or r in q.parents


def run_check(check, root, evidence_manual=None, cid=None):
    """-> (result, detail) with result in pass|fail|unverified|error (error = could not be evaluated). Never raises on a failing check."""
    kind = check["kind"]
    try:
        if kind == "command":
            cwd = check.get("cwd", ".")
            if not _inside(root, cwd):
                return "error", f"cwd {cwd} escapes root"
            r = subprocess.run(check["argv"], cwd=Path(root) / cwd, capture_output=True, text=True, timeout=check.get("timeout", 120))
            ok = r.returncode == check.get("expect_exit", 0) and all(s in r.stdout for s in check.get("expect_stdout_contains", []))
            if ok:
                return "pass", f"exit {r.returncode}"
            tail = ((r.stdout or "") + (r.stderr or "")).strip()[-600:]       # bounded evidence so a repair attempt knows WHY it failed
            return "fail", f"exit {r.returncode}" + (f"; output tail: {tail}" if tail else "")
        if kind == "file_exists":
            if not _inside(root, check["path"]):
                return "error", "path escapes root"
            return ("pass" if (Path(root) / check["path"]).exists() else "fail"), check["path"]
        if kind == "file_contains":
            if not _inside(root, check["path"]):
                return "error", "path escapes root"
            f = Path(root) / check["path"]
            return ("pass" if f.is_file() and check["contains"] in f.read_text(errors="replace") else "fail"), check["path"]
        ref = (evidence_manual or {}).get(cid)
        return ("pass", f"manual confirmation: {ref}") if ref else ("unverified", "manual criterion with no recorded confirmation")
    except (OSError, subprocess.TimeoutExpired, KeyError) as e:
        return "error", f"{type(e).__name__}: {e}"


def validate_scores(rubric, scores):
    """Delegates to scoring.py (the single scoring implementation). -> (problems, weighted normalized value)."""
    prof = scoring.load_profile(dict(rubric))
    problems = scoring.validate_ratings(prof, scores or {})
    return problems, (None if problems else scoring.score(prof, scores)["weighted_normalized"])


def assess(contract, root=".", evidence=None, attempts_used=0):
    evidence = evidence or {}
    bad = validate_contract(contract)
    if bad:
        return {"complete": False, "recommended": "fix_contract", "problems": bad}
    criteria, incomplete = [], []
    for a in contract["acceptance"]:
        res, detail = run_check(a["check"], root, evidence.get("manual_confirmations"), a["id"])
        req = a.get("required", True)
        criteria.append({"id": a["id"], "required": req, "result": res, "detail": detail, "evidence_ref": evidence.get("refs", {}).get(a["id"])})
        if req and res != "pass":
            incomplete.append(a["id"])
    hits, unevaluated = [], []
    for f in contract["failure_conditions"]:
        res, detail = run_check(f["check"], root, evidence.get("manual_confirmations"), f["id"])
        if res == "pass":      # a passing failure-condition check means the failure occurred
            hits.append({"id": f["id"], "detail": detail})
        elif res in ("unverified", "error"):
            unevaluated.append({"id": f["id"], "detail": detail})   # could not be evaluated: fail closed
    usage = evidence.get("usage") or {}
    tokens = usage.get("total_tokens")             # None = unknown, never zero
    budget = contract["budget"]
    blockers, limitations = [], list(evidence.get("limitations", []))
    over = tokens is not None and "max_tokens" in budget and tokens > budget["max_tokens"]
    if over:
        blockers.append(f"token budget exceeded ({tokens} > {budget['max_tokens']})")
    if tokens is None:
        limitations.append("usage unknown: cost is not zero, it is unmeasured")
    out = {"v": 1, "work_id": contract["id"], "criteria": criteria, "failure_hits": hits, "incomplete": incomplete,
           "blockers": blockers, "limitations": limitations, "usage": {"total_tokens": tokens, "source": usage.get("source", "not supplied")},
           "unevaluated_failure_conditions": unevaluated, "complete": not incomplete and not hits and not unevaluated}
    if contract.get("rubric"):
        probs, norm = validate_scores(contract["rubric"], evidence.get("scores"))
        out["scores"] = {"rubric_id": contract["rubric"].get("id"), "normalized": None if probs else norm, "raw": evidence.get("scores"), "problems": probs,
                         "note": "scores do not alter completeness or authorization"}
    auth = contract["authorization"]
    out["integration_allowed"] = out["complete"] and not blockers and auth.get("may_merge") is True
    if blockers:
        out["recommended"] = "blocked"
    elif out["complete"]:
        out["recommended"] = "accept"
    elif attempts_used >= budget["max_attempts"]:      # no execution attempt left to repair with
        out["recommended"] = "escalate"
    else:
        out["recommended"] = "repair"
    texts = {a["id"]: a for a in contract["acceptance"]}
    detail = {c["id"]: c["detail"] for c in criteria}
    out["repair_instructions"] = [f"criterion {i} not met: {texts[i].get('text', '')} -- {detail.get(i, '')}".strip() for i in incomplete] + [f"failure condition {h['id']} occurred" for h in hits] + [f"failure condition {u['id']} could not be evaluated" for u in unevaluated]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("contract")
    a = sub.add_parser("assess"); a.add_argument("contract"); a.add_argument("--root", default="."); a.add_argument("--evidence"); a.add_argument("--attempts-used", type=int, default=0)
    ns = ap.parse_args(argv)
    c = json.loads(Path(ns.contract).read_text())
    if ns.cmd == "validate":
        out = {"problems": validate_contract(c)}
        print(json.dumps(out, indent=1)); return 1 if out["problems"] else 0
    ev = json.loads(Path(ns.evidence).read_text()) if ns.evidence else None
    out = assess(c, ns.root, ev, ns.attempts_used)
    print(json.dumps(out, indent=1))
    return 0 if out["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
