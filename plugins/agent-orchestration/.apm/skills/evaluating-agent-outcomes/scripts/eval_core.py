#!/usr/bin/env python3
"""Reusable evaluation core (stdlib only): store, proportionate selection, fixtures, pilot, validity, costs,
human interventions, repair records. Single authoritative implementation; callers (including Sanctuary's adapter) import it.

Storage is always an explicit JSONL file inside a declared root (default root: cwd, default file: <root>/.agent-work/records.jsonl).
Nothing is written to a global location. Missing measurements stay None/unknown, never zero.
"""
import json, re, subprocess, time
from pathlib import Path

SCHEMA = 1
INTERVENTION_CATEGORIES = ("required_authorization", "necessary_clarification", "execution_failure_correction", "scope_change")
COST_CATEGORIES = ("execution", "orchestration_review", "retry_failed", "verification", "repair")
DEFAULT_STORE = ".agent-work/records.jsonl"
LEGACY_KINDS = {"HUMAN_INTERVENTION": "intervention", "FAILURE_REPAIR": "repair", "REPAIR_APPLICATION": "repair_application"}
LEGACY_EVENT_TYPES = {v: k for k, v in LEGACY_KINDS.items()}


# ------------------------------------------------------------------ storage (bounded)
def resolve_store(root=".", store=None):
    r = Path(root).resolve()
    p = Path(store) if store else Path(DEFAULT_STORE)
    p = (p if p.is_absolute() else r / p).resolve()
    if p != r and r not in p.parents:
        raise ValueError(f"store {p} is outside the declared root {r}")
    return p


def append(kind, record, root=".", store=None, compat_event_type=False):
    p = resolve_store(root, store)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"v": SCHEMA, "kind": kind, **record, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())}
    if compat_event_type:
        rec["event_type"] = LEGACY_EVENT_TYPES.get(kind, kind.upper())
    with p.open("a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def load(root=".", store=None):
    p = resolve_store(root, store)
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict):
            e.setdefault("kind", LEGACY_KINDS.get(e.get("event_type")))
            out.append(e)
    return out


# ------------------------------------------------------------------ proportionate selection
def select_method(deterministic_checkable, consequential, uncertain, preregistered_requirements_unmet=False):
    """Cheapest adequate method. A preregistered requirement that cannot be afforded is checkpointed, never reduced."""
    if preregistered_requirements_unmet:
        return {"method": "checkpoint", "why": "state the exact remaining requirement; never shrink a preregistered experiment to fit a budget"}
    if deterministic_checkable:
        return {"method": "deterministic", "why": "schema, executable, unique-id, ownership, state-transition, arithmetic or artifact checks settle it"}
    if consequential and uncertain:
        return {"method": "controlled_research", "why": "consequential and uncertain: preregister, freeze, then run"}
    return {"method": "bounded_model_review", "why": "interpretation that deterministic assertions cannot settle"}


# ------------------------------------------------------------------ fixtures before responses
def run_fixtures(fixtures, cwd="."):
    """fixtures: [{name, argv, [stdin], expect_exit, [expect_stdout_contains]}]. All must pass before model calls."""
    results = []
    for fx in fixtures:
        p = subprocess.run(fx["argv"], input=fx.get("stdin"), text=True, capture_output=True, cwd=cwd, timeout=fx.get("timeout", 60))
        ok = p.returncode == fx.get("expect_exit", 0) and all(s in p.stdout for s in fx.get("expect_stdout_contains", []))
        results.append({"name": fx["name"], "passed": ok, "exit": p.returncode})
    return {"passed": all(r["passed"] for r in results), "results": results}


# ------------------------------------------------------------------ output-contract pilot
def pilot_adherence(responses, pattern, min_adherence=0.8, confirmatory_ids=()):
    rx = re.compile(pattern)
    n = len(responses)
    ok = sum(1 for r in responses if rx.search(r.get("text") or ""))
    overlap = sorted({r["id"] for r in responses} & set(confirmatory_ids))
    adherence = ok / n if n else 0.0
    problems = []
    if adherence < min_adherence:
        problems.append(f"pilot adherence {adherence:.2f} < {min_adherence}: fix the output contract on development items, then pilot again")
    if overlap:
        problems.append(f"pilot ids reused as confirmatory items: {overlap[:5]}")
    return {"adherence": round(adherence, 4), "adherent": ok, "n": n, "problems": problems, "ready": not problems}


# ------------------------------------------------------------------ benchmark validity
def validity(planned, valid, arms, min_adherence=0.8, ceiling=0.98):
    """What may a finished benchmark claim? Malformed/missing answers stay in `planned`; low adherence caps the claim at mechanics;
    a floor/ceiling or absent baseline is unscorable."""
    problems, notes = [], []
    if not isinstance(planned, int) or planned <= 0 or not isinstance(valid, int) or not 0 <= valid <= planned:
        raise ValueError("need integer planned > 0 and 0 <= valid <= planned")
    if not 0.5 <= min_adherence <= 1.0:
        raise ValueError("min_adherence must be within [0.5, 1.0]; a weaker bar defeats the gate")
    for name, a in arms.items():
        if not 0 <= a["k"] <= a["n"] or a["n"] <= 0:
            raise ValueError(f"arm {name}: need 0 <= k <= n and n > 0")
    adherence = valid / planned
    if not arms:
        problems.append("UNINTERPRETABLE_BASELINE")
        notes.append("no baseline arm supplied: the behavior rate cannot be interpreted")
    if adherence < min_adherence:
        problems.append("ADHERENCE_LIMITED")
        notes.append(f"only {valid}/{planned} answers met the output contract ({adherence:.2f}); the intended behavior is unobservable "
                     "for the rest, so behavioral corroboration may not be claimed (report mechanics and adherence only)")
    for name, a in arms.items():
        rate = a["k"] / a["n"]
        if rate == 0.0 or rate >= ceiling:
            problems.append("UNINTERPRETABLE_BASELINE")
            notes.append(f"arm {name}: rate {a['k']}/{a['n']} sits at the floor/ceiling; a reduction (or gain) cannot be measured")
    problems = sorted(set(problems))
    claim = "BEHAVIORAL_CLAIM_ALLOWED" if not problems else ("MECHANICS_ONLY" if "ADHERENCE_LIMITED" in problems else "UNSCORABLE")
    return {"adherence": round(adherence, 4), "problems": problems, "max_claim": claim, "notes": notes}


# ------------------------------------------------------------------ interventions / repairs
def record_intervention(category, reason, observed_event, mission=None, root=".", store=None, compat_event_type=False):
    """Interventions come from observable events (a user message), never from model self-report."""
    if category not in INTERVENTION_CATEGORIES:
        raise ValueError(f"category must be one of {INTERVENTION_CATEGORIES}")
    if not observed_event:
        raise ValueError("observed_event is required: cite the user message or event, not an inference")
    return append("intervention", {"category": category, "reason": reason, "observed_event": observed_event, "mission_id": mission,
                                   "counts_as_correction": category == "execution_failure_correction"}, root, store, compat_event_type)


def record_repair(category, evidence, repair, verification, owner, cause="suspected", existing_guard=None, repair_cost_tokens=None,
                  root=".", store=None, compat_event_type=False):
    if not (category and evidence and owner):
        raise ValueError("category, evidence and owner are required: a repair record cites an observed failure")
    return append("repair", {"category": category, "evidence": evidence, "cause": cause, "existing_guard": existing_guard, "repair": repair,
                             "verification": verification, "owner": owner, "repair_cost_tokens": repair_cost_tokens}, root, store, compat_event_type)


def record_application(category, outcome, unit, root=".", store=None, compat_event_type=False):
    """outcome: prevented | recurred | not_applicable. Recurrence counts applicable opportunities only."""
    if outcome not in ("prevented", "recurred", "not_applicable"):
        raise ValueError("outcome must be prevented|recurred|not_applicable")
    return append("repair_application", {"category": category, "outcome": outcome, "unit": unit}, root, store, compat_event_type)


def repair_report(root=".", store=None):
    cats = {}
    for e in load(root, store):
        t = e.get("kind")
        if t not in ("repair", "repair_application", "intervention"):
            continue
        c = cats.setdefault(e.get("category"), {"failures": 0, "repairs": 0, "prevented": 0, "recurred": 0, "interventions": 0})
        if t == "repair":
            c["failures"] += 1
            c["repairs"] += 1 if e.get("repair") else 0
        elif t == "repair_application":
            if e.get("outcome") in ("prevented", "recurred"):
                c[e["outcome"]] += 1
        else:
            c["interventions"] += 1
    for c in cats.values():
        opp = c["prevented"] + c["recurred"]
        c["opportunities"] = opp
        c["recurrence_rate"] = round(c["recurred"] / opp, 4) if opp else None
        c["repair_due"] = c["failures"] >= 2 and c["repairs"] == 0
    return cats


def intervention_summary(root=".", store=None):
    """Counts by category plus coverage: absent records are 'unknown', not zero interventions."""
    recs = [e for e in load(root, store) if e.get("kind") == "intervention"]
    by = {k: 0 for k in INTERVENTION_CATEGORIES}
    for e in recs:
        if e.get("category") in by:
            by[e["category"]] += 1
    return {"by_category": by, "corrections": by["execution_failure_correction"], "records": len(recs),
            "coverage": "recorded events only; sessions without recording are unknown, not zero" if not recs else "partial: recorded events only"}


def investment(units):
    """units: [{id, execution, orchestration_review, retry_failed, verification, repair}] tokens; None/missing = unknown.
    Callers must not double-count nested workers (attribute a worker's tokens once, to its own unit)."""
    totals = {k: None for k in COST_CATEGORIES}
    unknown = {k: [] for k in COST_CATEGORIES}
    for u in units:
        for k in COST_CATEGORIES:
            v = u.get(k)
            if v is None:
                unknown[k].append(u.get("id"))
            elif isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
                raise ValueError(f"unit {u.get('id')}: {k} must be a non-negative number")
            else:
                totals[k] = (totals[k] or 0) + v
    if not units:
        return {"totals": totals, "unknown_units": {}, "telemetry_gap": True, "overhead_share_of_known": None, "note": "no units supplied"}
    known_total = sum(v for v in totals.values() if v is not None)
    overhead = (totals["orchestration_review"] or 0) + (totals["verification"] or 0)
    return {"totals": totals, "totals_are_lower_bounds": any(unknown.values()),
            "unknown_units": {k: v for k, v in unknown.items() if v}, "telemetry_gap": any(unknown.values()),
            "overhead_share_of_known": round(overhead / known_total, 4) if known_total else None,
            "unit": "tokens (subscription usage); API-equivalent price estimates are a separate quantity and are not mixed in"}
