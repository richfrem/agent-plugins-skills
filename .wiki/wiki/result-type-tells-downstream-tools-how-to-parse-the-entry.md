---
concept: result-type-tells-downstream-tools-how-to-parse-the-entry
source: plugin-code
source_file: agent-agentic-os/scripts/experiment_log.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.698540+00:00
cluster: path
content_hash: 76f4d7443046cf96
---

# result_type tells downstream tools how to parse the entry

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
    Catches interleaved shell output or wrong fi

*(content truncated)*

## See Also

- [[1-parse-the-hook-payload]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[function-parse-xml-to-markdown]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/experiment_log.py`
- **Indexed:** 2026-04-27T05:21:03.698540+00:00
