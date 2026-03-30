"""
update_ranked_skills.py

CLI utility to update or add entries in summary-ranked-skills.json.
Used by the eval-autoresearch-fit skill after completing an assessment.

Usage:
    # Update scores for an existing entry
    python update_ranked_skills.py \\
        --plugin agent-execution-disciplines \\
        --skill verification-before-completion \\
        --objectivity 8 --speed 7 --frequency 10 --utility 10 \\
        --verdict HIGH \\
        --loop-type LLM_IN_LOOP \\
        --evaluator-command "python evaluate.py --skill SKILL.md --tasks tasks/ --trials 5" \\
        --mutation-target "SKILL.md" \\
        --barriers "Needs golden task set" "LLM non-determinism requires N=5 averaging" \\
        --eval-notes "Goodhart risk: must verify Bash call is a real test command" \\
        --status EVALUATED

    # Add a new entry
    python update_ranked_skills.py \\
        --plugin my-plugin \\
        --skill my-skill \\
        --objectivity 7 --speed 9 --frequency 5 --utility 6 \\
        --verdict MEDIUM \\
        --proposed-benchmark "Exit code from pytest run" \\
        --justification "Fast loop, objective metric" \\
        --status PENDING

    # Show current entry
    python update_ranked_skills.py --plugin my-plugin --skill my-skill --show

    # List all entries with status
    python update_ranked_skills.py --list

    # List only entries matching a status
    python update_ranked_skills.py --list --filter-status EVALUATED

    # Show next 3 highest-scored unevaluated entries (for structured batch)
    python update_ranked_skills.py --next-batch 3

    # Pick 3 random unevaluated entries (for sampling / ad-hoc testing)
    python update_ranked_skills.py --random 3
"""

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path


# Default path relative to this script's location
DEFAULT_JSON_PATH = Path(__file__).parent.parent / "assets" / "resources" / "summary-ranked-skills.json"


def load_json(path: Path) -> dict:
    """Load the ranked skills JSON file."""
    if not path.exists():
        print(f"ERROR: JSON file not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: Path) -> None:
    """Save the ranked skills JSON file, preserving order."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_entry(skills: list, plugin: str, skill: str) -> tuple[int, dict | None]:
    """Find an entry by plugin+skill name. Returns (index, entry) or (-1, None)."""
    for i, entry in enumerate(skills):
        if entry.get("plugin") == plugin and entry.get("skill") == skill:
            return i, entry
    return -1, None


def compute_total(entry: dict) -> int:
    """Recompute total from the four score fields."""
    return (
        entry.get("objectivity_score", 0)
        + entry.get("execution_speed_score", 0)
        + entry.get("frequency_of_use_score", 0)
        + entry.get("potential_utility_score", 0)
    )


def verdict_from_total(total: int) -> str:
    """Derive viability verdict from total score."""
    if total >= 32:
        return "HIGH"
    elif total >= 24:
        return "MEDIUM"
    elif total >= 16:
        return "LOW"
    else:
        return "NOT_VIABLE"


def show_entry(entry: dict) -> None:
    """Pretty-print a single entry."""
    print(f"\n{'='*60}")
    print(f"  {entry['plugin']} / {entry['skill']}")
    print(f"{'='*60}")
    scores = {
        "objectivity": entry.get("objectivity_score", "-"),
        "speed": entry.get("execution_speed_score", "-"),
        "frequency": entry.get("frequency_of_use_score", "-"),
        "utility": entry.get("potential_utility_score", "-"),
    }
    total = entry.get("total_autoresearch_viability", "-")
    refined = entry.get("refined_total")
    print(f"  Scores: obj={scores['objectivity']} spd={scores['speed']} "
          f"freq={scores['frequency']} util={scores['utility']} -> total={total}"
          + (f" (refined={refined})" if refined else ""))
    print(f"  Verdict:         {entry.get('eval_verdict', entry.get('verdict', 'PENDING'))}")
    print(f"  Status:          {entry.get('status', 'PENDING')}")
    print(f"  Loop type:       {entry.get('loop_type', '-')}")
    if entry.get("eval_date"):
        print(f"  Eval date:       {entry['eval_date']}")
    if entry.get("mutation_target"):
        print(f"  Mutation target: {entry['mutation_target']}")
    if entry.get("evaluator_command"):
        print(f"  Evaluator cmd:   {entry['evaluator_command']}")
    if entry.get("key_barriers"):
        print("  Barriers:")
        for b in entry["key_barriers"]:
            print(f"    - {b}")
    if entry.get("eval_notes"):
        print(f"  Notes:           {entry['eval_notes']}")
    if entry.get("proposed_benchmark_metric"):
        print(f"  Benchmark:       {entry['proposed_benchmark_metric']}")
    print()


def list_all(skills: list, filter_status: str | None = None) -> None:
    """Print a summary table of all entries."""
    header = f"{'PLUGIN':<30} {'SKILL':<35} {'TOTAL':>5} {'VERDICT':<12} {'STATUS':<15} {'LOOP TYPE'}"
    print("\n" + header)
    print("-" * len(header))
    filtered = [s for s in skills if filter_status is None or s.get("status", "PENDING") == filter_status]
    filtered_sorted = sorted(filtered, key=lambda x: x.get("refined_total") or x.get("total_autoresearch_viability", 0), reverse=True)
    for s in filtered_sorted:
        total = s.get("refined_total") or s.get("total_autoresearch_viability", 0)
        verdict = s.get("eval_verdict", "PENDING")
        status = s.get("status", "PENDING")
        loop = s.get("loop_type", "-")
        print(f"  {s['plugin']:<28} {s['skill']:<33} {total:>5} {verdict:<12} {status:<15} {loop}")
    print(f"\n  Total: {len(filtered)} entries\n")


def unevaluated(skills: list) -> list:
    """Return skills whose status is PENDING (not yet evaluated, skipped, or in-progress)."""
    return [s for s in skills if s.get("status", "PENDING") == "PENDING"]


def next_batch(skills: list, n: int) -> list:
    """Return the top-N unevaluated skills by total_autoresearch_viability descending."""
    pending = unevaluated(skills)
    pending_sorted = sorted(
        pending,
        key=lambda x: x.get("total_autoresearch_viability", 0),
        reverse=True,
    )
    return pending_sorted[:n]


def random_batch(skills: list, n: int) -> list:
    """Return N randomly sampled unevaluated skills."""
    pending = unevaluated(skills)
    count = min(n, len(pending))
    return random.sample(pending, count)


def print_batch(batch: list, label: str) -> None:
    """Print a short summary of a batch of skills to evaluate next."""
    print(f"\n{label} ({len(batch)} skills):")
    print("-" * 60)
    for s in batch:
        total = s.get("total_autoresearch_viability", 0)
        print(f"  [{total:>2}] {s['plugin']} / {s['skill']}")
    print()
    print("Evaluate with:")
    for s in batch:
        print(f"  eval-autoresearch-fit  {s['plugin']}/{s['skill']}")
    print()


def morning_report(skills: list) -> None:
    """Print the full morning handoff: ranked table + debrief stats + top recommendation."""
    evaluated = [s for s in skills if s.get("status") == "EVALUATED"]
    pending   = [s for s in skills if s.get("status") == "PENDING"]
    skipped   = [s for s in skills if s.get("status") == "SKIPPED"]

    evaluated.sort(key=lambda x: x.get("refined_total") or x.get("total_autoresearch_viability", 0), reverse=True)

    verdict_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "NOT_VIABLE": 0}
    loop_counts    = {"DETERMINISTIC": 0, "LLM_IN_LOOP": 0, "HYBRID": 0}
    total_evals    = sum(s.get("eval_count", 1) for s in evaluated)

    for s in evaluated:
        v = s.get("eval_verdict", "")
        if v in verdict_counts:
            verdict_counts[v] += 1
        l = s.get("loop_type", "")
        if l in loop_counts:
            loop_counts[l] += 1

    print("\n" + "=" * 70)
    print("  ECOSYSTEM FITNESS SWEEP v1 — MORNING REPORT")
    print("=" * 70)
    print(f"  Evaluated:    {len(evaluated):>4}   (across {total_evals} total eval passes)")
    print(f"  Pending:      {len(pending):>4}")
    print(f"  Skipped:      {len(skipped):>4}")
    print(f"  Total skills: {len(skills):>4}")
    print()
    print(f"  Verdicts  →  HIGH: {verdict_counts['HIGH']}  MEDIUM: {verdict_counts['MEDIUM']}  LOW: {verdict_counts['LOW']}  NOT_VIABLE: {verdict_counts['NOT_VIABLE']}")
    print(f"  Loop types →  DETERMINISTIC: {loop_counts['DETERMINISTIC']}  LLM_IN_LOOP: {loop_counts['LLM_IN_LOOP']}  HYBRID: {loop_counts['HYBRID']}")
    print()
    print(f"  {'#':>3}  {'PLUGIN':<30} {'SKILL':<35} {'SCORE':>5}  {'VERDICT':<12} {'LOOP':<15} {'EVALS'}")
    print("  " + "-" * 105)
    for i, s in enumerate(evaluated, 1):
        score   = s.get("refined_total") or s.get("total_autoresearch_viability", 0)
        verdict = s.get("eval_verdict", "?")
        loop    = s.get("loop_type", "?")
        count   = s.get("eval_count", 1)
        marker  = " ★" if verdict == "HIGH" else "  "
        print(f"  {i:>3}{marker} {s['plugin']:<30} {s['skill']:<35} {score:>5}  {verdict:<12} {loop:<15} {count}x")

    print()
    top = [s for s in evaluated if s.get("eval_verdict") == "HIGH"]
    if not top:
        top = [s for s in evaluated if s.get("eval_verdict") == "MEDIUM"]

    if top:
        rec = top[0]
        score = rec.get("refined_total") or rec.get("total_autoresearch_viability", 0)
        print("=" * 70)
        print("  ★ RECOMMENDATION: NEXT AUTORESEARCH LOOP TO BUILD")
        print("=" * 70)
        print(f"  Skill:     {rec['plugin']}/{rec['skill']}")
        print(f"  Score:     {score}/40  |  Verdict: {rec.get('eval_verdict')}  |  Loop: {rec.get('loop_type','?')}")
        if rec.get("evaluator_command"):
            print(f"  Evaluator: {rec['evaluator_command']}")
        if rec.get("mutation_target"):
            print(f"  Mutates:   {rec['mutation_target']}")
        if rec.get("eval_notes"):
            print(f"  Why:       {rec['eval_notes']}")
        if len(top) > 1:
            print()
            print("  Also consider:")
            for s in top[1:4]:
                sc = s.get("refined_total") or s.get("total_autoresearch_viability", 0)
                print(f"    - {s['plugin']}/{s['skill']} ({sc}/40, {s.get('loop_type','?')})")
    print("=" * 70 + "\n")


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Update or inspect entries in summary-ranked-skills.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json-path", default=str(DEFAULT_JSON_PATH),
                        help="Path to summary-ranked-skills.json")
    parser.add_argument("--plugin", help="Plugin name")
    parser.add_argument("--skill", help="Skill name")

    # Score fields
    parser.add_argument("--objectivity", type=int, help="Objectivity score (1-10)")
    parser.add_argument("--speed", type=int, help="Execution speed score (1-10)")
    parser.add_argument("--frequency", type=int, help="Frequency of use score (1-10)")
    parser.add_argument("--utility", type=int, help="Potential utility score (1-10)")

    # Eval fields
    parser.add_argument("--verdict", choices=["HIGH", "MEDIUM", "LOW", "NOT_VIABLE"],
                        help="Autoresearch viability verdict")
    parser.add_argument("--loop-type",
                        choices=["DETERMINISTIC", "LLM_IN_LOOP", "HYBRID"],
                        help="Type of evaluation loop")
    parser.add_argument("--evaluator-command", help="The immutable shell command for scoring")
    parser.add_argument("--mutation-target", help="Which file the agent modifies per loop")
    parser.add_argument("--barriers", nargs="+", help="List of key barriers (space-separated strings)")
    parser.add_argument("--eval-notes", help="Free-text notes from the evaluation")
    parser.add_argument("--proposed-benchmark", help="Proposed benchmark metric description")
    parser.add_argument("--justification", help="Justification text")
    parser.add_argument("--status",
                        choices=["PENDING", "EVALUATED", "IN_PROGRESS", "IMPLEMENTED", "SKIPPED"],
                        help="Current status of this skill's autoresearch work")
    parser.add_argument("--refined-total", type=int,
                        help="Override total score after deeper evaluation")

    # Display commands
    parser.add_argument("--show", action="store_true", help="Show current entry and exit")
    parser.add_argument("--list", action="store_true", help="List all entries and exit")
    parser.add_argument("--filter-status", help="Filter --list output by status")
    parser.add_argument("--next-batch", type=int, metavar="N",
                        help="Show the top-N PENDING entries by score (structured batch order)")
    parser.add_argument("--random", type=int, metavar="N", dest="random_n",
                        help="Show N randomly sampled PENDING entries (for ad-hoc testing)")
    parser.add_argument("--morning-report", action="store_true",
                        help="Print full ranked summary sorted by score — the morning handoff table")

    args = parser.parse_args()
    json_path = Path(args.json_path)
    data = load_json(json_path)
    skills = data.get("skills", [])

    # Morning report mode
    if args.morning_report:
        morning_report(skills)
        return

    # List mode
    if args.list:
        list_all(skills, args.filter_status)
        return

    # Batch discovery modes (no plugin/skill required)
    if args.next_batch is not None:
        batch = next_batch(skills, args.next_batch)
        print_batch(batch, f"Next {args.next_batch} by score (PENDING)")
        return

    if args.random_n is not None:
        batch = random_batch(skills, args.random_n)
        print_batch(batch, f"{args.random_n} random PENDING entries")
        return

    # Require plugin + skill for all other operations
    if not args.plugin or not args.skill:
        parser.error("--plugin and --skill are required (unless using --list, --next-batch, or --random)")

    idx, entry = find_entry(skills, args.plugin, args.skill)

    # Show mode
    if args.show:
        if entry is None:
            print(f"No entry found for {args.plugin}/{args.skill}")
        else:
            show_entry(entry)
        return

    # Create entry if it doesn't exist
    if entry is None:
        print(f"Creating new entry: {args.plugin}/{args.skill}")
        entry = {"plugin": args.plugin, "skill": args.skill}
        skills.append(entry)
        idx = len(skills) - 1

    # Apply score fields
    if args.objectivity is not None:
        entry["objectivity_score"] = args.objectivity
    if args.speed is not None:
        entry["execution_speed_score"] = args.speed
    if args.frequency is not None:
        entry["frequency_of_use_score"] = args.frequency
    if args.utility is not None:
        entry["potential_utility_score"] = args.utility

    # Recompute total if any score changed
    if any(x is not None for x in [args.objectivity, args.speed, args.frequency, args.utility]):
        new_total = compute_total(entry)
        entry["total_autoresearch_viability"] = new_total
        if args.refined_total is None and args.verdict is None:
            # Auto-derive verdict from total if not explicitly set
            entry["eval_verdict"] = verdict_from_total(new_total)

    # Apply eval fields
    if args.refined_total is not None:
        entry["refined_total"] = args.refined_total
        if args.verdict is None:
            entry["eval_verdict"] = verdict_from_total(args.refined_total)
    if args.verdict is not None:
        entry["eval_verdict"] = args.verdict
    if args.loop_type is not None:
        entry["loop_type"] = args.loop_type
    if args.evaluator_command is not None:
        entry["evaluator_command"] = args.evaluator_command
    if args.mutation_target is not None:
        entry["mutation_target"] = args.mutation_target
    if args.barriers is not None:
        entry["key_barriers"] = args.barriers
    if args.eval_notes is not None:
        entry["eval_notes"] = args.eval_notes
    if args.proposed_benchmark is not None:
        entry["proposed_benchmark_metric"] = args.proposed_benchmark
    if args.justification is not None:
        entry["justification"] = args.justification
    if args.status is not None:
        entry["status"] = args.status

    # Stamp eval date and increment eval_count whenever eval fields are written
    eval_fields = [args.verdict, args.loop_type, args.evaluator_command,
                   args.mutation_target, args.eval_notes, args.status]
    if any(f is not None for f in eval_fields):
        entry["eval_date"] = str(date.today())
        entry["eval_count"] = entry.get("eval_count", 0) + 1

    # Write back
    data["skills"][idx] = entry
    save_json(data, json_path)
    print(f"Updated: {args.plugin}/{args.skill}")
    show_entry(entry)


if __name__ == "__main__":
    main()
