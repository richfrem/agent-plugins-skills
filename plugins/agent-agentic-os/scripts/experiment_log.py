#!/usr/bin/env python3
"""
experiment_log.py — Evolution Experiment Log Manager

Persistent, folder-based log of all agentic-os experiment runs.
Each run writes one dated file to context/experiment-log/.
An index.md tracks all runs for fast querying.

Usage:
    python3 experiment_log.py append --source-type verifier [--report PATH] [--session-id ID] [--target NAME]
    python3 experiment_log.py append --source-type tester   [--report PATH] [--session-id ID] [--target NAME]
    python3 experiment_log.py append --source-type orchestrator [--report PATH] [--session-id ID] [--target NAME]
    python3 experiment_log.py append --source-type planner  [--report PATH] [--session-id ID] [--target NAME]
    python3 experiment_log.py query <term>
    python3 experiment_log.py summary

Source types and result kinds:
    verifier      os-evolution-verifier: EVOLUTION_VERIFICATION blocks      result_type=qualitative
    tester        os-architect-tester: AC-1–4 pass/fail scenario report     result_type=qualitative
    orchestrator  triple-loop-orchestrator: LOG_PROGRESS.md + wal.log       result_type=numeric
    planner       os-evolution-planner: task plan (workstreams + gaps)       result_type=qualitative
    survey        post_run_survey: session friction + north star metrics     result_type=mixed

Result type determines how downstream tools parse entries:
    numeric      → contains score fields (best_score, keeps, discards) suitable for chart/trend
    qualitative  → contains PASS/FAIL/PARTIAL verdicts and gap analysis prose
    mixed        → contains both; agents must check which fields are present before parsing
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("context/experiment-log")
INDEX_FILE = LOG_DIR / "index.md"

DEFAULT_REPORTS = {
    "verifier": Path("temp/os-evolution-verifier/test-report.md"),
    "tester": Path("temp/test_report_consolidated.md"),
    "orchestrator": Path("temp/logs/run-log.md"),
    "planner": None,   # path required for planner
    "survey": Path("context/memory/post_run_survey.md"),
}

# result_type tells downstream tools how to parse the entry
RESULT_TYPES = {
    "verifier": "qualitative",
    "tester": "qualitative",
    "orchestrator": "numeric",
    "planner": "qualitative",
    "survey": "mixed",
}

INDEX_HEADER = (
    "# Experiment Log Index\n\n"
    "| Date | Session ID | Source | Target | Result Type | Verdict | Detail |\n"
    "|------|------------|--------|--------|-------------|---------|--------|\n"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(INDEX_HEADER)


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def _dated_filename(source_type: str, session_id: str) -> Path:
    date = datetime.now().strftime("%Y-%m-%d")
    slug = _slugify(session_id)
    return LOG_DIR / f"{date}-{source_type}-{slug}.md"


def _read_report(path: Path) -> str:
    if not path.exists():
        print(f"ERROR: Report not found at {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text()


def _append_index_row(date: str, session_id: str, source: str, target: str,
                       result_type: str, verdict: str, filename: Path):
    row = (f"| {date} | {session_id} | {source} | {target} "
           f"| {result_type} | {verdict} | [{filename.name}]({filename.name}) |\n")
    with INDEX_FILE.open("a") as f:
        f.write(row)


# ---------------------------------------------------------------------------
# Parsers — extract key metrics from each source type
# ---------------------------------------------------------------------------

def _parse_verifier(text: str) -> dict:
    verdicts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0}
    for m in re.findall(r"VERDICT:\s*(PASS|PARTIAL|FAIL)", text):
        verdicts[m] += 1
    total = sum(verdicts.values())
    verdict_str = f"{verdicts['PASS']}P/{verdicts['PARTIAL']}Pa/{verdicts['FAIL']}F of {total}"
    return {"verdicts": verdicts, "total": total, "verdict_str": verdict_str}


def _parse_tester(text: str) -> dict:
    passes = len(re.findall(r"\bPASS\b", text))
    fails = len(re.findall(r"\bFAIL\b", text))
    total = passes + fails
    scenarios = len(re.findall(r"(?m)^## (?:Scenario|TEST)", text))
    verdict_str = f"{passes}P/{fails}F of {total} ACs"
    return {"passes": passes, "fails": fails, "total": total,
            "scenarios": scenarios, "verdict_str": verdict_str}


def _parse_orchestrator(text: str) -> dict:
    keeps = len(re.findall(r"\bKEEP\b", text))
    discards = len(re.findall(r"\bDISCARD\b", text))
    scores = re.findall(r"\b0\.\d+\b", text)
    best = max((float(s) for s in scores), default=0.0)
    baseline_match = re.search(r"[Bb]aseline[:\s]+([0-9.]+)", text)
    baseline = float(baseline_match.group(1)) if baseline_match else 0.0
    delta = round(best - baseline, 4)
    verdict_str = f"{keeps}K/{discards}D baseline={baseline:.3f} best={best:.3f} delta={delta:+.3f}"
    return {"keeps": keeps, "discards": discards, "best_score": best,
            "baseline": baseline, "delta": delta, "verdict_str": verdict_str}


def _parse_planner(text: str) -> dict:
    workstreams = len(re.findall(r"(?m)^\| WS-[A-Z]", text))
    gaps = len(re.findall(r"(?m)^- \*\*", text))
    verdict_str = f"{workstreams} workstreams, {gaps} gaps"
    return {"workstreams": workstreams, "gaps": gaps, "verdict_str": verdict_str}


def _parse_survey(text: str) -> dict:
    friction = len(re.findall(r"(?m)^[-*]\s+.+friction", text, re.I))
    north_star_match = re.search(r"[Nn]orth.star[:\s]+([0-9.]+)%?", text)
    north_star = north_star_match.group(1) if north_star_match else "?"
    verdict_str = f"friction_items={friction} north_star={north_star}"
    return {"friction_items": friction, "north_star": north_star, "verdict_str": verdict_str}


PARSERS = {
    "verifier": _parse_verifier,
    "tester": _parse_tester,
    "orchestrator": _parse_orchestrator,
    "planner": _parse_planner,
    "survey": _parse_survey,
}


# ---------------------------------------------------------------------------
# Entry builder
# ---------------------------------------------------------------------------

def _build_entry(source_type: str, session_id: str, target: str,
                  triggered_by: str, report_text: str, metrics: dict,
                  result_type: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"---\n"
        f"type: {source_type}\n"
        f"result_type: {result_type}\n"
        f"date: {timestamp}\n"
        f"session_id: {session_id}\n"
        f"source: {triggered_by}\n"
        f"target: {target}\n"
        f"verdict: {metrics['verdict_str']}\n"
        f"---\n\n"
        f"## Experiment — {timestamp} | {source_type} | {target}\n\n"
        f"| Field | Value |\n"
        f"|-------|-------|\n"
        f"| Session ID | {session_id} |\n"
        f"| Source | {triggered_by} |\n"
        f"| Target | {target} |\n"
        f"| Result type | {result_type} |\n"
        f"| Verdict | {metrics['verdict_str']} |\n\n"
        f"---\n\n"
        f"{report_text.strip()}\n\n"
        f"---\n\n"
        f"### Actions Taken\n"
        f"_[fill in: what was done in response to failures — spec fix, new eval, new skill]_\n"
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_append(args):
    source_type = args.source_type
    if source_type not in PARSERS:
        print(f"ERROR: unknown source-type '{source_type}'. "
              f"Valid: {', '.join(PARSERS)}", file=sys.stderr)
        sys.exit(1)

    report_path = Path(args.report) if args.report else DEFAULT_REPORTS[source_type]
    if report_path is None:
        print(f"ERROR: --report PATH is required for source-type '{source_type}'", file=sys.stderr)
        sys.exit(1)

    report_text = _read_report(report_path)
    metrics = PARSERS[source_type](report_text)
    session_id = args.session_id or datetime.now().strftime("%Y-%m-%d-%H%M")
    target = args.target or "unknown"
    triggered_by = args.triggered_by or source_type

    result_type = RESULT_TYPES[source_type]
    _ensure_log_dir()
    filename = _dated_filename(source_type, session_id)
    entry = _build_entry(source_type, session_id, target, triggered_by,
                          report_text, metrics, result_type)
    filename.write_text(entry)

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    _append_index_row(date_str, session_id, source_type, target,
                       result_type, metrics["verdict_str"], filename)

    print(f"Logged to {filename}")
    print(f"Index updated: {INDEX_FILE}")
    print(f"Verdict: {metrics['verdict_str']}")


def cmd_query(args):
    _ensure_log_dir()
    term = args.term.lower()
    matches = []

    for f in sorted(LOG_DIR.glob("*.md")):
        if f.name == "index.md":
            continue
        text = f.read_text()
        if term in text.lower():
            # Extract header block for context
            header_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
            header = header_match.group(1) if header_match else "(no header)"
            matches.append((f.name, header))

    if not matches:
        print(f"No matches for '{term}' in {LOG_DIR}/")
        return

    print(f"Found {len(matches)} file(s) matching '{term}':\n")
    for fname, header in matches:
        print(f"### {fname}")
        print(header)
        print()


def cmd_summary(args: argparse.Namespace) -> None:
    del args
    _ensure_log_dir()

    files = [f for f in sorted(LOG_DIR.glob("*.md")) if f.name != "index.md"]
    if not files:
        print(f"No experiment runs found in {LOG_DIR}/")
        return

    by_type: dict[str, list] = {}
    total_runs = 0

    for f in files:
        text = f.read_text()
        header_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not header_match:
            continue
        header = dict(
            line.split(": ", 1) for line in header_match.group(1).splitlines()
            if ": " in line
        )
        src = header.get("type", "unknown")
        verdict = header.get("verdict", "?")
        by_type.setdefault(src, []).append(verdict)
        total_runs += 1

    print(f"Experiment Log Summary — {LOG_DIR}/")
    print(f"  Total runs: {total_runs}")
    print()

    for src, verdicts in sorted(by_type.items()):
        print(f"  [{src}] — {len(verdicts)} run(s)")
        for v in verdicts:
            print(f"    {v}")

    print(f"\n  Index: {INDEX_FILE}")
    print(f"  Files: {len(files)}")


def main():
    parser = argparse.ArgumentParser(description="Evolution experiment log manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser("append", help="Append a run report to the experiment log")
    ap.add_argument("--source-type", required=True,
                    choices=sorted(PARSERS.keys()),
                    help="Which component produced the report")
    ap.add_argument("--report", help="Path to the report file")
    ap.add_argument("--session-id", help="Session identifier (used in filename)")
    ap.add_argument("--target", help="Skill/agent under test")
    ap.add_argument("--triggered-by", help="Agent or skill that triggered the run")

    qp = sub.add_parser("query", help="Search experiment log files")
    qp.add_argument("term", help="Search term (scenario ID, verdict, keyword)")

    sub.add_parser("summary", help="Print aggregate statistics across all runs")

    args = parser.parse_args()

    if args.cmd == "append":
        cmd_append(args)
    elif args.cmd == "query":
        cmd_query(args)
    elif args.cmd == "summary":
        cmd_summary(args)


if __name__ == "__main__":
    main()
