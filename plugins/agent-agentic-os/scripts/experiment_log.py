#!/usr/bin/env python3
"""
experiment_log.py — Evolution Experiment Log Manager

Persistent, folder-based log of all agentic-os experiment runs.
Each run writes one dated file to context/experiment-log/.
An index.md tracks all runs for fast querying.

Usage:
    python3 experiment_log.py append --source-type verifier [--report PATH] [--session-id ID] [--target NAME] [--tags TAG1,TAG2]
    python3 experiment_log.py append --source-type tester   [--report PATH] [--session-id ID] [--target NAME] [--tags TAG1,TAG2]
    python3 experiment_log.py append --source-type orchestrator [--report PATH] [--session-id ID] [--target NAME] [--tags TAG1,TAG2]
    python3 experiment_log.py append --source-type planner  [--report PATH] [--session-id ID] [--target NAME] [--tags TAG1,TAG2]
    python3 experiment_log.py query <term>
    python3 experiment_log.py summary
    python3 experiment_log.py synthesize [--last N] [--output PATH]

Source types and result kinds:
    verifier      os-evolution-verifier: EVOLUTION_VERIFICATION blocks      result_type=qualitative
    tester        os-architect-tester: AC-1–4 pass/fail scenario report     result_type=qualitative
    orchestrator  triple-loop-orchestrator: LOG_PROGRESS.md + wal.log       result_type=numeric
    planner       os-evolution-planner: task plan (workstreams + gaps)       result_type=qualitative
    survey        post_run_survey: session friction + north star metrics     result_type=mixed

Result type determines how downstream tools parse entries:
    numeric      → score fields (best_score, keeps, discards, delta) suitable for chart/trend
    qualitative  → PASS/FAIL/PARTIAL verdicts and gap analysis prose
    mixed        → both; agents must check which fields are present before parsing
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

# Expected header tokens to validate report files before parsing
EXPECTED_HEADERS = {
    "verifier": ["EVOLUTION_VERIFICATION", "os-evolution-verifier"],
    "tester": ["os-architect Test Report", "AC-"],
    "orchestrator": ["LOG_PROGRESS", "KEEP", "DISCARD"],
    "planner": ["## Workstreams", "WS-"],
    "survey": [],  # surveys have no fixed header
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


def _validate_report(source_type: str, text: str) -> None:
    """Abort if the report doesn't look like the expected format.
    Catches interleaved shell output or wrong file passed as --report."""
    tokens = EXPECTED_HEADERS.get(source_type, [])
    if not tokens:
        return
    if not any(tok in text for tok in tokens):
        print(
            f"ERROR: Report for source-type '{source_type}' does not contain expected "
            f"header tokens: {tokens}\n"
            f"First 200 chars of file:\n{text[:200]}",
            file=sys.stderr,
        )
        sys.exit(1)


def _session_already_logged(session_id: str) -> bool:
    """Return True if session_id already appears in index.md."""
    if not INDEX_FILE.exists():
        return False
    return session_id in INDEX_FILE.read_text()


def _append_index_row(date: str, session_id: str, source: str, target: str,
                       result_type: str, verdict: str, filename: Path):
    row = (f"| {date} | {session_id} | {source} | {target} "
           f"| {result_type} | {verdict} | [{filename.name}]({filename.name}) |\n")
    with INDEX_FILE.open("a") as f:
        f.write(row)


def _extract_section(text: str, start_heading: str) -> str:
    """Extract text from start_heading to the next same-level heading (or EOF)."""
    m = re.match(r"^(#+)", start_heading)
    level = len(m.group(1)) if m else 1
    next_heading = re.compile(rf"^#{{1,{level}}} ", re.MULTILINE)
    start = text.find(start_heading)
    if start == -1:
        return ""
    body_start = text.find("\n", start) + 1
    rest = text[body_start:]
    end_match = next_heading.search(rest)
    return rest[: end_match.start()] if end_match else rest


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
    # Restrict PASS/FAIL scan to the Results table section only
    section = _extract_section(text, "## Results")
    if not section:
        section = text  # fallback if format differs
    passes = len(re.findall(r"\bPASS\b", section))
    fails = len(re.findall(r"\bFAIL\b", section))
    # N/A rows don't count toward total
    total = passes + fails
    scenarios = len(re.findall(r"(?m)^## (?:Scenario|TEST|Overall)", text))
    verdict_str = f"{passes}P/{fails}F of {total} ACs"
    return {"passes": passes, "fails": fails, "total": total,
            "scenarios": scenarios, "verdict_str": verdict_str}


def _parse_orchestrator(text: str) -> dict:
    """Parse LOG_PROGRESS.md markdown table — column-aware, not free-text float scan."""
    keeps = 0
    discards = 0
    scores: list[float] = []

    for line in text.splitlines():
        # Match markdown table data rows: | iter | score | verdict | reason |
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) >= 3:
            verdict_cell = cells[2].upper()
            score_cell = cells[1]
            if verdict_cell == "KEEP":
                keeps += 1
                try:
                    scores.append(float(score_cell))
                except ValueError:
                    pass
            elif verdict_cell == "DISCARD":
                discards += 1

    best = max(scores, default=0.0)
    baseline_match = re.search(r"[Bb]aseline[:\s]+([0-9.]+)", text)
    baseline = float(baseline_match.group(1)) if baseline_match else (scores[0] if scores else 0.0)
    delta = round(best - baseline, 4)
    verdict_str = f"{keeps}K/{discards}D baseline={baseline:.3f} best={best:.3f} delta={delta:+.3f}"
    return {"keeps": keeps, "discards": discards, "best_score": best,
            "baseline": baseline, "delta": delta, "verdict_str": verdict_str}


def _parse_planner(text: str) -> dict:
    workstreams = len(re.findall(r"(?m)^\| WS-[A-Z]", text))
    # Restrict gap count to the Gaps Identified section only
    gaps_section = _extract_section(text, "## Gaps Identified")
    gaps = len(re.findall(r"(?m)^[-*]\s+", gaps_section)) if gaps_section else 0
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
                  result_type: str, tags: str = "") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    tags_line = f"tags: {tags}\n" if tags else ""
    return (
        f"---\n"
        f"type: {source_type}\n"
        f"result_type: {result_type}\n"
        f"date: {timestamp}\n"
        f"session_id: {session_id}\n"
        f"source: {triggered_by}\n"
        f"target: {target}\n"
        f"verdict: {metrics['verdict_str']}\n"
        f"{tags_line}"
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
              f"Valid: {', '.join(sorted(PARSERS))}", file=sys.stderr)
        sys.exit(1)

    report_path = Path(args.report) if args.report else DEFAULT_REPORTS[source_type]
    if report_path is None:
        print(f"ERROR: --report PATH is required for source-type '{source_type}'", file=sys.stderr)
        sys.exit(1)

    report_text = _read_report(report_path)
    _validate_report(source_type, report_text)

    session_id = args.session_id or datetime.now().strftime("%Y-%m-%d-%H%M")
    target = args.target or "unknown"
    triggered_by = args.triggered_by or source_type

    _ensure_log_dir()

    # Idempotency guard — abort if this session was already logged
    if _session_already_logged(session_id):
        print(
            f"WARNING: session '{session_id}' already appears in {INDEX_FILE}.\n"
            f"Use --session-id with a unique value to log a second run, or "
            f"remove the existing entry first.",
            file=sys.stderr,
        )
        sys.exit(1)

    metrics = PARSERS[source_type](report_text)
    result_type = RESULT_TYPES[source_type]
    tags = getattr(args, "tags", "") or ""
    filename = _dated_filename(source_type, session_id)
    entry = _build_entry(source_type, session_id, target, triggered_by,
                          report_text, metrics, result_type, tags)
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
            header_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
            header = header_match.group(1) if header_match else "(no header)"
            # Also surface Actions Taken for FAIL entries
            actions_match = re.search(r"### Actions Taken\n(.*?)(?=\n---|$)", text, re.DOTALL)
            actions = actions_match.group(1).strip() if actions_match else ""
            matches.append((f.name, header, actions))

    if not matches:
        print(f"No matches for '{term}' in {LOG_DIR}/")
        return

    print(f"Found {len(matches)} file(s) matching '{term}':\n")
    for fname, header, actions in matches:
        print(f"### {fname}")
        print(header)
        if actions and "_[fill in" not in actions:
            print(f"\nActions Taken:\n{actions}")
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


def cmd_synthesize(args: argparse.Namespace) -> None:
    """Query last N entries and produce a structured synthesis block."""
    _ensure_log_dir()
    last_n = getattr(args, "last", 5) or 5

    files = [f for f in sorted(LOG_DIR.glob("*.md")) if f.name != "index.md"]
    if not files:
        print(f"No experiment runs found in {LOG_DIR}/")
        return

    recent = files[-last_n:]

    by_target: dict[str, dict] = {}
    for f in recent:
        text = f.read_text()
        header_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not header_match:
            continue
        header = dict(
            line.split(": ", 1) for line in header_match.group(1).splitlines()
            if ": " in line
        )
        target = header.get("target", "unknown")
        session_id = header.get("session_id", f.stem)
        verdict = header.get("verdict", "?")
        tags = header.get("tags", "")
        entry = by_target.setdefault(target, {"keeps": [], "discards": [], "sessions": []})
        entry["sessions"].append(session_id)
        # Count KEEP/DISCARD from verdict string or raw iteration lines
        keeps = len(re.findall(r"\bKEEP\b", text))
        discards = len(re.findall(r"\bDISCARD\b", text))
        if keeps > discards:
            entry["keeps"].append((session_id, verdict, tags))
        elif discards > 0:
            entry["discards"].append((session_id, verdict, tags))

    date_str = datetime.now().strftime("%Y-%m-%d")
    lines = [f"## SYNTHESIZED LEARNINGS — {date_str}", ""]

    lines.append("### Patterns that consistently improve performance")
    any_keep = False
    for target, data in sorted(by_target.items()):
        for session_id, verdict, tags in data["keeps"]:
            # Extract positive delta from verdict_str if present
            delta_match = re.search(r"delta=([+\-][0-9.]+)", verdict)
            delta_str = f"avg delta {delta_match.group(1)}" if delta_match else "see verdict"
            tag_str = f" [{tags}]" if tags else ""
            lines.append(f"- {target} → seen in {session_id}, {delta_str}{tag_str}")
            any_keep = True
    if not any_keep:
        lines.append("- (no KEEP patterns in last N entries)")

    lines.append("")
    lines.append("### Patterns that cause regressions")
    any_discard = False
    for target, data in sorted(by_target.items()):
        for session_id, verdict, tags in data["discards"]:
            delta_match = re.search(r"delta=([+\-][0-9.]+)", verdict)
            delta_str = f"avg delta {delta_match.group(1)}" if delta_match else "see verdict"
            tag_str = f" [{tags}]" if tags else ""
            lines.append(f"- {target} → seen in {session_id}, {delta_str}{tag_str}")
            any_discard = True
    if not any_discard:
        lines.append("- (no DISCARD patterns in last N entries)")

    lines.append("")
    lines.append("### Recommended updates to core skills")
    for target in sorted(by_target.keys()):
        data = by_target[target]
        if data["discards"]:
            lines.append(f"- {target} → review recent DISCARD patterns; consider prompt revision")
        elif data["keeps"]:
            lines.append(f"- {target} → stable; no immediate action required")

    synthesis_text = "\n".join(lines) + "\n"

    output_path_arg = getattr(args, "output", None)
    if output_path_arg:
        output_path = Path(output_path_arg)
    else:
        output_path = LOG_DIR / f"synthesis-{date_str}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(synthesis_text)
    print(f"Synthesis written to {output_path}")
    print(synthesis_text)


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
    ap.add_argument("--tags", help="Comma-separated tags (e.g. skill-improvement,overfitting-detected,path-b)")

    qp = sub.add_parser("query", help="Search experiment log files")
    qp.add_argument("term", help="Search term (scenario ID, verdict, keyword)")

    sub.add_parser("summary", help="Print aggregate statistics across all runs")

    sp = sub.add_parser("synthesize", help="Synthesize patterns from last N log entries")
    sp.add_argument("--last", type=int, default=5,
                    help="Number of most recent entries to include (default: 5)")
    sp.add_argument("--output", help="Output path (default: context/experiment-log/synthesis-[date].md)")

    args = parser.parse_args()

    if args.cmd == "append":
        cmd_append(args)
    elif args.cmd == "query":
        cmd_query(args)
    elif args.cmd == "summary":
        cmd_summary(args)
    elif args.cmd == "synthesize":
        cmd_synthesize(args)


if __name__ == "__main__":
    main()
