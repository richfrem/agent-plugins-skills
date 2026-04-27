---
concept: only-include-those-appearing-in-2-of-the-last-n-traces
source: plugin-code
source_file: agent-agentic-os/scripts/generate_milestone.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.279067+00:00
cluster: score
content_hash: 6e78e72774a7844a
---

# Only include those appearing in 2+ of the last N traces

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-agentic-os/scripts/generate_milestone.py -->
#!/usr/bin/env python
"""
generate_milestone.py -- Write milestone summary files for long autoresearch runs.
==================================================================================

Purpose:
    Reads evals/results.tsv and evals/traces/*.json for a skill experiment directory.
    Writes a milestone_NNN.md summary every N iterations (default: 25).
    Enables the proposer to read distant history without losing context — the
    Meta-Harness equivalent of proactive summarization (Lee et al., arXiv:2603.28052).

    This is a pure read-then-write utility. It does not affect KEEP/DISCARD decisions
    and must never be added to LOCKED_FILES in evaluate.py.

Usage:
    pythongenerate_milestone.py --experiment-dir <path> [--every 25] [--force]

    --experiment-dir   Path to the experiment directory (contains evals/ and references/)
    --every N          Write a milestone every N iterations (default: 25)
    --force            Write a milestone even if iteration count is not a multiple of --every

Output:
    evals/traces/milestone_NNN.md  where NNN = the iteration count at time of writing

Exit codes:
    0  Milestone written (or --force used)
    0  No milestone needed yet (iteration count not a multiple of --every, no --force)
    2  Error (bad path, missing results.tsv, etc.)
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_tsv(results_tsv: Path) -> list[dict]:
    if not results_tsv.exists():
        return []
    rows = []
    with open(results_tsv, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def _load_traces(traces_dir: Path) -> list[dict]:
    """Load all iter_*.json trace files, sorted by name."""
    traces = []
    if not traces_dir.exists():
        return traces
    for path in sorted(traces_dir.glob("iter_*.json")):
        try:
            traces.append(json.loads(path.read_text()))
        except Exception:
            pass
    return traces


def _best_keeps(iter_rows: list[dict], top_n: int = 3) -> list[str]:
    """Return descriptions of the top-N highest-delta KEEP iterations."""
    keep_rows = [r for r in iter_rows if r.get("status") == "KEEP"]
    keep_rows_sorted = sorted(keep_rows, key=lambda r: float(r.get("score", 0)), reverse=True)
    results = []
    for row in keep_rows_sorted[:top_n]:
        desc = row.get("description", "(no description)")
        score = float(row.get("score", 0))
        baseline = float(row.get("baseline", 0))
        delta = score - baseline
        results.append(f"  - +{delta:.4f}: \"{desc}\" (score={score:.4f})")
    return results


def _worst_discards(iter_rows: list[dict], top_n: int = 3) -> list[str]:
    """Return descriptions of the top-N most negative-delta DISCARD iterations, with failure reasons."""
    discard_rows = [r for r in iter_rows if r.get("status") == "DISCARD"]
    discard_rows_sorted = sorted(discard_rows, key=lambda r: float(r.get("score", 0)))
    results = []
    seen_descs: dict[str, int] = {}
    for row in discard_rows_sorted[:top_n]:
        desc = row.get("description", "(no description)")
        seen_descs[desc] = seen_descs.get(desc, 0) + 1
    for row in discard_rows_sorted[:top_n]:
        desc = row.get("description", "(no description)")
        score = float(row.get("score", 0))
        baseline = float(row.get("baseline", 0))
        delta = score - baseline
        repeat = f" [tried {seen_descs[desc]}x]" if seen_descs.get(desc, 1) > 1 else ""
        results.append(f"  - {delta:.4f}: \"{desc}\"{repeat} (score={score:.4f})")
    return results


def _current_fp_fn(traces: list[dict]) -> tuple[float | None, float | None, int, int, int, int]:
    """Return (fp_rate, fn_rate, fp, fn, total_false, total_true) from the most recent trace."""
    for trace in reversed(traces):
        detail = trace.get("routing_detail", [])
        if not detail:
       

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/os-eval-runner/scripts/generate_milestone.py -->
#!/usr/bin/env python3
"""
generate_milestone.py -- Write milestone summary files for long autoresearch runs.
==================================================================================

Purpose:
    Reads evals/results.tsv and evals/traces/*.json for a skill experiment directory.
    Writes a milestone_NNN.md summary every N iterations (default: 25).
    Enables the proposer to read distant history without losing context — the
    Meta-Harness equivalent of proactive summarization (Lee et al., arXiv:2603.28052).

    This is a pure read-then-write utility. It does not affect KEEP/DISCARD decisions
    and must never be added to LOCKED_FILES in evaluate.py.

Usage:
    python3 generate_milestone.py --experiment-dir <path> [--every 25] [--force]

    --experiment-dir   Path t

*(combined content truncated)*

## See Also

- [[only-check-files-in-pluginsskills]]
- [[thin-wrapper-delegates-to-the-canonical-implementation-in-scripts]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-parse-the-hook-payload]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/generate_milestone.py`
- **Indexed:** 2026-04-27T05:21:04.279067+00:00
