#!/usr/bin/env python3
"""Profile-driven scoring: the single authoritative generic implementation (stdlib only).

A PROFILE (JSON data) names the dimensions, their scale and weights, how the headline number is computed, and an optional
model-cost "bloat" rule. Callers keep their own meanings by supplying their own profile; nothing here encodes a project's rubric.
Historical records stay valid because the arithmetic is unchanged: `raw_fraction` fitness = round(sum/ max_sum, 3).

Profile:  {"id","dimensions":{name:{"max":int,"weight":num}},"fitness":"raw_fraction"|"weighted",
           "bloat":{"min_weight":3.0,"low_dimensions":{name:threshold},"message":"... {model} ... {weight} ..."}}
"""
import json
from pathlib import Path


def load_profile(src):
    p = src if isinstance(src, dict) else json.loads(Path(src).read_text())
    if not p.get("dimensions"):
        raise ValueError("profile needs dimensions")
    for n, d in p["dimensions"].items():
        if not isinstance(d.get("max"), int) or d["max"] <= 0:
            raise ValueError(f"dimension {n}: max must be a positive integer")
    p.setdefault("fitness", "weighted")
    return p


def max_score(profile):
    return sum(d["max"] for d in profile["dimensions"].values())


def validate_ratings(profile, ratings):
    problems = []
    for n, d in profile["dimensions"].items():
        v = (ratings or {}).get(n)
        if v is None:
            problems.append(f"dimension '{n}' not scored")
        elif isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= d["max"]:
            problems.append(f"{n}={v} outside 0..{d['max']}")
    extra = set(ratings or {}) - set(profile["dimensions"])
    problems += [f"unknown dimension '{x}'" for x in sorted(extra)]
    return problems


def score(profile, ratings, ndigits=3):
    """-> {dimensions, raw_score, max_score, fitness, weighted_normalized}. Raises ValueError on invalid ratings."""
    bad = validate_ratings(profile, ratings)
    if bad:
        raise ValueError("; ".join(bad))
    dims = {n: ratings[n] for n in profile["dimensions"]}
    raw, mx = sum(dims.values()), max_score(profile)
    wsum = sum(d.get("weight", 1) for d in profile["dimensions"].values()) or 1
    weighted = sum(d.get("weight", 1) * dims[n] / d["max"] for n, d in profile["dimensions"].items()) / wsum
    fitness = round(raw / float(mx), ndigits) if profile["fitness"] == "raw_fraction" else round(weighted, 4)
    return {"dimensions": dims, "raw_score": raw, "max_score": mx, "fitness": fitness, "weighted_normalized": round(weighted, 4)}


def cost_adjusted(fitness, weight, ndigits=3):
    return round(fitness / weight, ndigits)


def bloat_warning(profile, ratings, model, weight):
    rule = profile.get("bloat")
    if not rule or weight < rule["min_weight"]:
        return None
    if any(ratings[n] <= t for n, t in rule["low_dimensions"].items()):
        return rule["message"].format(model=model, weight=weight)
    return None


# ---- event-log projection (deterministic fold; order-independent rebuild)
def empty_projection(profile):
    return {"schema_version": 1, "updated_at": None, "total_assessments": 0, "cumulative_score": 0, "average_fitness": 0.0,
            "dimension_totals": {n: 0 for n in profile["dimensions"]}, "agents": {}, "recent_assessments": []}


def fold_assessment(profile, data, a, recent_limit=20):
    mx = float(max_score(profile))
    data["total_assessments"] = data.get("total_assessments", 0) + 1
    data["cumulative_score"] = data.get("cumulative_score", 0) + a["raw_score"]
    data["average_fitness"] = round(data["cumulative_score"] / (data["total_assessments"] * mx), 3)
    dt = data.setdefault("dimension_totals", {})
    for d, v in a["dimensions"].items():
        dt[d] = dt.get(d, 0) + v
    ag = data.setdefault("agents", {}).setdefault(a["agent_id"], {"assessments": 0, "cumulative_score": 0, "average_fitness": 0.0})
    ag["assessments"] += 1
    ag["cumulative_score"] += a["raw_score"]
    ag["average_fitness"] = round(ag["cumulative_score"] / (ag["assessments"] * mx), 3)
    recent = data.setdefault("recent_assessments", [])
    recent.insert(0, {"assessment_id": a["assessment_id"], "timestamp": a["timestamp"], "task_id": a["task_id"], "agent_id": a["agent_id"],
                      "raw_score": a["raw_score"], "fitness": a["cognitive_fitness"], "notes": a["notes"]})
    data["recent_assessments"] = recent[:recent_limit]
    return data


def rebuild_projection(profile, assessments):
    ordered = sorted(assessments, key=lambda a: (a["timestamp"], a["assessment_id"]))
    data = empty_projection(profile)
    for a in ordered:
        fold_assessment(profile, data, a)
    if ordered:
        data["updated_at"] = ordered[-1]["timestamp"]
    return data
