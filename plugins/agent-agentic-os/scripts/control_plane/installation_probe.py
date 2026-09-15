"""
control_plane/installation_probe.py -- Installation & Schema-Parity Classifier
===================================================================================

Purpose:
    Read-only Agentic OS installation and SQLite/source-parity classifier. Checks
    that the required repo substrates (control_plane.db, hooks.json, pre-commit
    evolution guard, CI workflow) exist, and that an existing control_plane.db's
    schema version and valid_transitions rows match the source-of-truth
    ALLOWED_TRANSITIONS DAG, reporting COMPLETE/PARTIAL/MISSING with the specific
    findings.

Key Input Dependencies:
    - `target` -- the repo root to classify (checked for REQUIRED_SUBSTRATES).
    - context/control_plane.db (if present) -- read-only, compared against
      CURRENT_SCHEMA_VERSION and ALLOWED_TRANSITIONS.

Key Functions:
    - REQUIRED_SUBSTRATES -- the 4 repo-relative paths a complete install requires.
    - InstallationProbeResult -- frozen dataclass of classification state + findings.
    - _expected_transitions() -- flattens ALLOWED_TRANSITIONS into (from, to) pairs.
    - _database_findings() -- compares an existing DB's schema/transitions against
      the source of truth, returning a list of drift findings.
    - classify_target() -- top-level entry point: runs the full substrate + DB check
      against `target` and returns the InstallationProbeResult.
"""

from __future__ import annotations

import sqlite3
import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

# When invoked as a standalone skill script, Python puts this directory—not its
# parent package directory—on sys.path. Add the package root for both layouts.
_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from control_plane.adapters import CURRENT_SCHEMA_VERSION, LEGAL_INITIAL_STATES
from control_plane.state_machine import ALLOWED_TRANSITIONS


REQUIRED_SUBSTRATES = (
    "context/control_plane.db",
    ".claude/hooks/hooks.json",
    ".git/hooks/pre-commit-evolution-guard",
    ".github/workflows/verify-evolution-integrity.yml",
)


@dataclass(frozen=True)
class InstallationProbeResult:
    state: str
    missing: tuple[str, ...]


def _expected_transitions() -> set[tuple[str | None, str]]:
    edges: set[tuple[str | None, str]] = {(source, target) for source, targets in ALLOWED_TRANSITIONS.items() for target in targets}
    return edges | {(None, s) for s in LEGAL_INITIAL_STATES}


def _database_findings(db_path: Path) -> list[str]:
    findings: list[str] = []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        version = conn.execute("SELECT version FROM schema_version ORDER BY rowid DESC LIMIT 1").fetchone()
        if not version or version[0] != CURRENT_SCHEMA_VERSION:
            findings.append(f"schema version drift (expected {CURRENT_SCHEMA_VERSION})")
        rows = conn.execute("SELECT from_state, to_state FROM valid_transitions").fetchall()
        if set(rows) != _expected_transitions():
            findings.append("valid transition rows drift from state_machine.py")
        trigger = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='trigger' AND name='enforce_valid_transition'"
        ).fetchone()
        if not trigger:
            findings.append("missing enforce_valid_transition trigger")
        conn.close()
    except (OSError, sqlite3.Error) as exc:
        findings.append(f"control-plane database unreadable: {exc}")
    return findings


def classify_target(target: Path) -> InstallationProbeResult:
    """Classify without creating, migrating, or modifying any target files."""
    root = target.resolve()
    present = [root / rel for rel in REQUIRED_SUBSTRATES if (root / rel).exists()]
    if not present:
        return InstallationProbeResult("FRESH", ())
    findings = [f"missing substrate: {rel}" for rel in REQUIRED_SUBSTRATES if not (root / rel).exists()]
    db_path = root / "context/control_plane.db"
    if db_path.exists():
        findings.extend(_database_findings(db_path))
    if findings:
        return InstallationProbeResult("PARTIAL_OR_DRIFTED", tuple(findings))
    return InstallationProbeResult("COMPLETE", ())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify an Agentic OS installation read-only.")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = classify_target(args.target)
    print(json.dumps({"state": result.state, "missing": list(result.missing)}))
