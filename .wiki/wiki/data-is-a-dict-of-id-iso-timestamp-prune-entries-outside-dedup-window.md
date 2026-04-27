---
concept: data-is-a-dict-of-id-iso-timestamp-prune-entries-outside-dedup-window
source: plugin-code
source_file: exploration-cycle-plugin/hooks/event_subscriber.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.975041+00:00
cluster: event
content_hash: 0558949b0f068129
---

# data is a dict of {id: iso_timestamp}; prune entries outside dedup window

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
event_subscriber.py
=====================================

Purpose:
    Reads events.jsonl and prints any unprocessed events matching a given action.
    Marks processed events by writing their content-hash IDs to a sidecar file so
    they are not re-surfaced on the next hook invocation.

Layer: Hooks / Triggering

Usage Examples:
    python hooks/event_subscriber.py --action suggest_intake --since 300 --dedup-window 3600

Supported Object Types:
    - Events (.jsonl)

CLI Arguments:
    --action: The event action string to match.
    --since: Only consider events emitted within the last N seconds (default: 300).
    --dedup-window: Remember processed event IDs for N seconds (default: 3600).

Input Files:
    - events.jsonl

Output:
    - Printed matched events.

Key Functions:
    - event_id()
    - load_processed()
    - save_processed()

Script Dependencies:
    None

Consumed by:
    - Exploration cycle hooks
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path

KERNEL_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / "context"
EVENTS_FILE = KERNEL_DIR / "events.jsonl"
PROCESSED_FILE = KERNEL_DIR / ".processed_events"


def event_id(event: dict) -> str:
    """Stable ID based on content hash — survives log rotation."""
    raw = json.dumps(event, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def load_processed(dedup_cutoff_ts: float) -> set:
    """Load processed IDs, pruning entries older than the dedup window."""
    if not PROCESSED_FILE.exists():
        return set()
    try:
        data = json.loads(PROCESSED_FILE.read_text())
        # data is a dict of {id: iso_timestamp}; prune entries outside dedup window
        return {k for k, ts in data.items() if _parse_ts(ts) >= dedup_cutoff_ts}
    except Exception:
        return set()


def save_processed(id_ts_map: dict) -> None:
    PROCESSED_FILE.write_text(json.dumps(id_ts_map))


def _parse_ts(ts_str: str) -> float:
    try:
        return datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Exploration Cycle kernel event subscriber")
    parser.add_argument("--action", required=True, help="Event action to match (e.g. suggest_intake)")
    parser.add_argument("--since", type=int, default=300,
                        help="Only consider events emitted within the last N seconds (recency filter, default: 300)")
    parser.add_argument("--dedup-window", type=int, default=3600, dest="dedup_window",
                        help="Remember processed event IDs for N seconds (dedup TTL, default: 3600)")
    args = parser.parse_args()

    if not EVENTS_FILE.exists():
        sys.exit(1)

    now = time.time()
    cutoff = now - args.since              # recency: how old an event can be to be considered
    dedup_cutoff = now - args.dedup_window # dedup TTL: how long to remember processed IDs
    processed = load_processed(dedup_cutoff)
    matched = []
    all_id_ts: dict = {}

    try:
        lines = EVENTS_FILE.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"[event_subscriber] Could not read events file: {e}", file=sys.stderr)
        sys.exit(1)

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        eid = event_id(event)
        ts = _parse_ts(event.get("time", ""))

        # Track all recent events for sidecar update
        if ts >= cutoff:
            all_id_ts[eid] = event.get("time", "")

        if eid in processed:
            continue
        if event.get("action") != args.action:
            continue
        if ts < cutoff:
            continue

        matched.append((eid, event))

    if not matched:
  

*(content truncated)*

## See Also

- [[extract-row-count-if-data-has-a-recognizable-structure]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[as-a-library]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[audit-a-single-file]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/hooks/event_subscriber.py`
- **Indexed:** 2026-04-27T05:21:03.975041+00:00
