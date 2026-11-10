#!/usr/bin/env python3
"""Lightweight lesson records on the explicit store from eval_core (stdlib only): add, find, use, stats.

A lesson: trigger, failure, evidence, cause (known|suspected), action, verification, limits, tags. `find` returns a few COMPACT
matches (never the whole history). Uses are recorded with outcomes so usefulness can be measured later.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_core as core

_STOP = {"the", "a", "an", "of", "to", "in", "for", "and", "or", "is", "on", "with", "when", "task", "work"}


def _tokens(text):
    return {t for t in re.findall(r"[a-z0-9_]+", (text or "").lower()) if t not in _STOP and len(t) > 2}


def add(trigger, failure, evidence, action, verification, limits, cause_status="suspected", cause="", tags=(), root=".", store=None):
    if not (trigger and failure and evidence and action):
        raise ValueError("trigger, failure, evidence and action are required: a lesson is specific and evidenced")
    if cause_status not in ("known", "suspected"):
        raise ValueError("cause_status must be known|suspected")
    lid = "L-" + hashlib.sha256((trigger + action).encode()).hexdigest()[:8]
    return core.append("lesson", {"id": lid, "trigger": trigger, "failure": failure, "evidence": evidence, "cause": {"status": cause_status, "text": cause},
                                  "action": action, "verification": verification, "limits": limits, "tags": list(tags)}, root, store)


def find(query, k=3, root=".", store=None):
    q = _tokens(query)
    scored = []
    for e in core.load(root, store):
        if e.get("kind") != "lesson":
            continue
        t = _tokens(e["trigger"] + " " + " ".join(e.get("tags", [])) + " " + e["failure"])
        s = len(q & t)
        if s:
            scored.append((s, e))
    scored.sort(key=lambda x: -x[0])
    return [{"id": e["id"], "trigger": e["trigger"], "action": e["action"], "limits": e.get("limits"), "cause": e["cause"]["status"], "evidence": e.get("evidence"), "match": s}
            for s, e in scored[:k]]


def brief_section(found, max_chars=1200, max_lessons=3):
    """Bounded text block for a worker brief. Lessons are FALLIBLE guidance: the block says so and cannot override the task's scope,
    acceptance criteria or authorization. Returns (text, supplied_ids); text is "" when there is nothing relevant."""
    if not found:
        return "", []
    head = ("## Lessons from earlier work (fallible guidance)\n"
            "Use only where they apply. They NEVER override this task's scope, acceptance criteria or authorization; if one conflicts, ignore it and say so.\n")
    out, ids = head, []
    for l in found[:max_lessons]:
        item = (f"- [{l['id']}] When: {l['trigger']}\n  Do: {l['action']}\n  Limits: {l.get('limits') or 'not stated'}"
                f" | cause {l.get('cause', 'unknown')} | evidence: {l.get('evidence') or 'none recorded'}\n")
        if len(out) + len(item) > max_chars:
            if not ids:                                  # always supply at least one, truncated
                item = item[: max(0, max_chars - len(out) - 4)] + "...\n"
            else:
                break
        out += item; ids.append(l["id"])
    return out, ids


def use(lesson_id, unit, outcome, root=".", store=None):
    if outcome not in ("helped", "no_effect", "harmful", "not_applicable"):
        raise ValueError("outcome must be helped|no_effect|harmful|not_applicable")
    if not any(e.get("kind") == "lesson" and e.get("id") == lesson_id for e in core.load(root, store)):
        raise ValueError(f"unknown lesson {lesson_id}")
    return core.append("lesson_use", {"lesson_id": lesson_id, "unit": unit, "outcome": outcome}, root, store)


def stats(root=".", store=None):
    out = {}
    for e in core.load(root, store):
        if e.get("kind") == "lesson":
            out.setdefault(e["id"], {"trigger": e["trigger"], "uses": 0, "helped": 0, "no_effect": 0, "harmful": 0})
    for e in core.load(root, store):
        if e.get("kind") == "lesson_use" and e["lesson_id"] in out:
            o = out[e["lesson_id"]]
            if e["outcome"] != "not_applicable":
                o["uses"] += 1
                o[e["outcome"]] += 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="."); ap.add_argument("--store")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    for n in ("trigger", "failure", "evidence", "action", "verification", "limits"):
        a.add_argument("--" + n, required=n in ("trigger", "failure", "evidence", "action"))
    a.add_argument("--cause-status", default="suspected"); a.add_argument("--cause", default=""); a.add_argument("--tag", action="append", default=[])
    f = sub.add_parser("find"); f.add_argument("query"); f.add_argument("-k", type=int, default=3)
    u = sub.add_parser("use"); u.add_argument("lesson_id"); u.add_argument("--unit", required=True); u.add_argument("--outcome", required=True)
    sub.add_parser("stats")
    ns = ap.parse_args(argv)
    if ns.cmd == "add":
        out = add(ns.trigger, ns.failure, ns.evidence, ns.action, ns.verification, ns.limits, ns.cause_status, ns.cause, ns.tag, ns.root, ns.store)
    elif ns.cmd == "find":
        out = find(ns.query, ns.k, ns.root, ns.store)
    elif ns.cmd == "use":
        out = use(ns.lesson_id, ns.unit, ns.outcome, ns.root, ns.store)
    else:
        out = stats(ns.root, ns.store)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
