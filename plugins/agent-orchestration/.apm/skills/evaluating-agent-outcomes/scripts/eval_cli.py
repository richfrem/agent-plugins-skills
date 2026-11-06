#!/usr/bin/env python3
"""CLI for eval_core gates: select | fixtures | pilot | validity | intervention | repair | invest | summary."""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_core as c


def _j(p):
    return json.loads(Path(p).read_text())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="."); ap.add_argument("--store")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select"); s.add_argument("--deterministic", action="store_true"); s.add_argument("--consequential", action="store_true")
    s.add_argument("--uncertain", action="store_true"); s.add_argument("--unaffordable-preregistered", action="store_true")
    f = sub.add_parser("fixtures"); f.add_argument("file"); f.add_argument("--cwd", default=".")
    p = sub.add_parser("pilot"); p.add_argument("file"); p.add_argument("--pattern", required=True); p.add_argument("--min-adherence", type=float, default=0.8)
    p.add_argument("--confirmatory-ids")
    v = sub.add_parser("validity"); v.add_argument("file"); v.add_argument("--min-adherence", type=float, default=0.8)
    i = sub.add_parser("intervention"); i.add_argument("--category", required=True, choices=c.INTERVENTION_CATEGORIES)
    i.add_argument("--reason", required=True); i.add_argument("--observed-event", required=True); i.add_argument("--mission")
    r = sub.add_parser("repair"); r.add_argument("action", choices=["record", "applied", "report"])
    for n in ("category", "evidence", "repair", "verification", "owner", "outcome", "unit"):
        r.add_argument("--" + n)
    r.add_argument("--cause", default="suspected", choices=["suspected", "confirmed"]); r.add_argument("--cost-tokens", type=int)
    n_ = sub.add_parser("invest"); n_.add_argument("file")
    sub.add_parser("summary")
    a = ap.parse_args(argv)
    kw = {"root": a.root, "store": a.store}
    if a.cmd == "select": out = c.select_method(a.deterministic, a.consequential, a.uncertain, a.unaffordable_preregistered)
    elif a.cmd == "fixtures": out = c.run_fixtures(_j(a.file), a.cwd)
    elif a.cmd == "pilot": out = c.pilot_adherence(_j(a.file), a.pattern, a.min_adherence, _j(a.confirmatory_ids) if a.confirmatory_ids else ())
    elif a.cmd == "validity":
        d = _j(a.file); out = c.validity(d["planned"], d["valid"], d.get("arms", {}), a.min_adherence)
    elif a.cmd == "intervention": out = c.record_intervention(a.category, a.reason, a.observed_event, a.mission, **kw)
    elif a.cmd == "repair":
        if a.action == "record": out = c.record_repair(a.category, a.evidence, a.repair, a.verification, a.owner, a.cause, repair_cost_tokens=a.cost_tokens, **kw)
        elif a.action == "applied": out = c.record_application(a.category, a.outcome, a.unit, **kw)
        else: out = c.repair_report(**kw)
    elif a.cmd == "invest": out = c.investment(_j(a.file))
    else: out = {"interventions": c.intervention_summary(**kw), "repairs": c.repair_report(**kw)}
    print(json.dumps(out, indent=1, sort_keys=True))
    bad = (a.cmd == "fixtures" and not out["passed"]) or (a.cmd == "pilot" and not out["ready"]) or (a.cmd == "validity" and out["max_claim"] != "BEHAVIORAL_CLAIM_ALLOWED")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
