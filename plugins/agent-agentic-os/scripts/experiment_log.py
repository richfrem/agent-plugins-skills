#!/usr/bin/env python3
"""
experiment_log.py — Evolution Experiment Log Manager

Persistent append-only log of os-evolution-verifier test runs.
Log lives at context/experiment-log.md and accumulates across sessions.

Usage:
    python3 experiment_log.py append [--report PATH] [--session-id ID] [--triggered-by AGENT]
    python3 experiment_log.py query <term>
    python3 experiment_log.py summary

Modes:
    append   Read test-report.md (or --report PATH) and append to experiment log
    query    Search log by scenario ID, verdict, or keyword
    summary  Print aggregate PASS/PARTIAL/FAIL counts and top failure modes
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("context/experiment-log.md")
DEFAULT_REPORT = Path("temp/os-evolution-verifier/test-report.md")


def _read_report(report_path: Path) -> str:
    if not report_path.exists():
        print(f"ERROR: Report not found at {report_path}", file=sys.stderr)
        sys.exit(1)
    return report_path.read_text()


def _ensure_log():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text(
            "# Experiment Log — os-evolution-verifier\n\n"
            "Persistent record of all evolution verification test runs.\n"
            "Append-only. Each entry fenced by `---`.\n\n---\n"
        )


def _parse_verdicts(text: str) -> dict:
    counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0}
    for match in re.findall(r"VERDICT:\s*(PASS|PARTIAL|FAIL)", text):
        counts[match] += 1
    return counts


def _parse_outputs_declared(text: str) -> int:
    vals = re.findall(r"OUTPUTS_DECLARED:\s*(\d+)", text)
    return sum(int(v) for v in vals)


def _parse_outputs_verified(text: str) -> int:
    vals = re.findall(r"OUTPUTS_VERIFIED:\s*(\d+)", text)
    return sum(int(v) for v in vals)


def cmd_append(args):
    report_path = Path(args.report) if args.report else DEFAULT_REPORT
    report_text = _read_report(report_path)
    verdicts = _parse_verdicts(report_text)
    total = sum(verdicts.values())

    _ensure_log()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    triggered_by = args.triggered_by or "os-evolution-verifier"
    session_id = args.session_id or timestamp.replace(" ", "-")

    entry = (
        f"\n## Experiment Run — {timestamp}\n\n"
        f"**Session ID**: {session_id}  \n"
        f"**Triggered by**: {triggered_by}  \n"
        f"**Scenarios run**: {total}  \n"
        f"**Verdicts**: "
        f"PASS: {verdicts['PASS']} | PARTIAL: {verdicts['PARTIAL']} | FAIL: {verdicts['FAIL']}\n\n"
        f"{report_text.strip()}\n\n"
        "### Actions Taken\n"
        "_[fill in: what was done in response to failures — spec fix, new eval, new skill]_\n\n"
        "---\n"
    )

    with LOG_PATH.open("a") as f:
        f.write(entry)

    print(
        f"Appended {total} scenario results to {LOG_PATH}\n"
        f"Verdicts: PASS={verdicts['PASS']} PARTIAL={verdicts['PARTIAL']} FAIL={verdicts['FAIL']}"
    )


def cmd_query(args):
    _ensure_log()
    text = LOG_PATH.read_text()
    term = args.term
    lines = text.splitlines()
    results = []
    for i, line in enumerate(lines):
        if term.lower() in line.lower():
            start = max(0, i - 2)
            end = min(len(lines), i + 15)
            results.append("\n".join(lines[start:end]))

    if not results:
        print(f"No matches for '{term}' in {LOG_PATH}")
        return

    print(f"Found {len(results)} match(es) for '{term}':\n")
    for r in results:
        print(r)
        print("---")


def cmd_summary(args: argparse.Namespace) -> None:
    del args  # summary takes no extra arguments
    _ensure_log()
    text = LOG_PATH.read_text()

    runs = len(re.findall(r"^## Experiment Run", text, re.MULTILINE))
    verdicts = _parse_verdicts(text)
    total_declared = _parse_outputs_declared(text)
    total_verified = _parse_outputs_verified(text)

    notes = re.findall(r"NOTES:\s*(.+)", text)
    note_counts: dict[str, int] = {}
    for note in notes:
        note = note.strip()
        if note and note.lower() not in ("none", "n/a", ""):
            note_counts[note] = note_counts.get(note, 0) + 1

    top_notes = sorted(note_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"Experiment Log Summary — {LOG_PATH}")
    print(f"  Total runs:        {runs}")
    print(f"  PASS:              {verdicts['PASS']}")
    print(f"  PARTIAL:           {verdicts['PARTIAL']}")
    print(f"  FAIL:              {verdicts['FAIL']}")
    if runs > 0:
        total_v = sum(verdicts.values())
        pass_rate = round(verdicts["PASS"] / total_v * 100) if total_v else 0
        print(f"  Pass rate:         {pass_rate}%")
    print(f"  Outputs declared:  {total_declared}")
    print(f"  Outputs verified:  {total_verified}")
    if top_notes:
        print("\n  Top failure notes:")
        for note, count in top_notes:
            print(f"    [{count}x] {note}")


def main():
    parser = argparse.ArgumentParser(description="Evolution experiment log manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser("append", help="Append test report to experiment log")
    ap.add_argument("--report", help="Path to test-report.md (default: temp/os-evolution-verifier/test-report.md)")
    ap.add_argument("--session-id", help="Session identifier")
    ap.add_argument("--triggered-by", help="Agent or skill that triggered the run")

    qp = sub.add_parser("query", help="Search experiment log")
    qp.add_argument("term", help="Search term (scenario ID, verdict, keyword)")

    sub.add_parser("summary", help="Print aggregate statistics")

    args = parser.parse_args()

    if args.cmd == "append":
        cmd_append(args)
    elif args.cmd == "query":
        cmd_query(args)
    elif args.cmd == "summary":
        cmd_summary(args)


if __name__ == "__main__":
    main()
