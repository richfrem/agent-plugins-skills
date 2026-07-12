#!/usr/bin/env python3
"""Non-interactive probe script for commonly used AI CLIs.
Safe: uses --version or a benign sub-command where available.

Purpose:
    Check which AI CLI tools (Agy, Copilot, Cursor) are installed and
    responsive, then write a summary report to environment_probe_report.txt.

Key Input Dependencies:
    - PATH (via shutil.which) for each CLI binary in PROBES
"""

import subprocess
import shutil
import datetime
import sys

REPORT_FILE = "environment_probe_report.txt"

PROBES = [
    ("Agy CLI (gemini replacement)", ["agy", "--version"]),
    ("Copilot CLI", ["gh", "copilot", "explain", "test"]),
    ("Cursor CLI", ["cursor", "--version"]),
]


def check_cmd(name: str, cmd: list[str]) -> None:
    """Probe a single CLI: check it's on PATH, then run cmd and return a summary line."""
    binary = cmd[0]
    print(f"Checking {name}...")
    if not shutil.which(binary):
        line = f"  x {name}: not installed"
        print(line)
        return line
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (result.stdout + result.stderr).strip()
        preview = "\n".join(output.splitlines()[:3])
        line = f"  v {name}: {preview}"
    except Exception as exc:
        line = f"  x {name}: probe failed ({exc})"
    print(line)
    return line


def main() -> None:
    """Probe every CLI in PROBES and write the results to REPORT_FILE."""
    timestamp = datetime.datetime.now().isoformat()
    lines = [f"Probing AI CLIs at {timestamp}"]
    print(lines[0])

    for name, cmd in PROBES:
        lines.append(check_cmd(name, cmd))

    lines.append("Probe complete.")
    print("Probe complete.")

    with open(REPORT_FILE, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Report written to {REPORT_FILE}")


if __name__ == "__main__":
    main()
