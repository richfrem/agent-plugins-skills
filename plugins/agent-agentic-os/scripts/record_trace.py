#!/usr/bin/env python
"""
record_trace.py — Safe Audit Manifest and Telemetry Logger
==========================================================

Purpose:
    Appends safe audit events conforming to Schema v1.1.0 to
    `.agent/learning/traces/cycle_manifests.jsonl` with previous-hash chaining.
    Maintains raw stdout/stderr in gitignored `.agent/learning/traces/raw/<cycle_id>/`
    with defense-in-depth secret scrubbing.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.1.0"
GENESIS_PREV_HASH = "0" * 64

EVENT_TYPES = [
    "cycle.initialized", "plan.completed", "authorization.granted",
    "worktree.created", "attempt.started", "mutation.completed",
    "verification.completed", "knowledge.persisted", "receipt.precommit.generated",
    "commit.completed", "rollback.completed", "receipt.final.generated",
    "cycle.completed", "cycle.escalated", "recovery.required"
]

CANONICAL_NODES = [
    "TRIAGE", "PLAN", "AWAITING_APPROVAL", "AUTHORIZED", "CREATE_WORKTREE",
    "EXECUTE", "VERIFY_GATE", "PRE_COMMIT_RECEIPT", "COMMIT", "ROLLBACK",
    "FINAL_RECEIPT", "COMPLETED", "ESCALATED", "RECOVERY_REQUIRED"
]


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_repo_root(repo_dir: Path = None) -> Path:
    if repo_dir:
        return repo_dir.resolve()
    try:
        res = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(res.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


def scrub_secrets(text: str) -> str:
    if not text:
        return ""
    # API keys
    text = re.sub(r"(sk-[a-zA-Z0-9_\-]{8,})", "[REDACTED_API_KEY]", text)
    text = re.sub(r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]", text)
    # Embedded credentials in URLs
    text = re.sub(r"(https?://)([^:/]+):([^@/]+)@", r"\1[REDACTED_USER]:[REDACTED_PASS]@", text)
    # Secret env lines
    text = re.sub(r"(?i)\b(API_KEY|API_SECRET|SECRET|TOKEN|PASSWORD|ACCESS_TOKEN)=([^\s\n]+)", r"\1=[REDACTED]", text)
    # Long base64-like blobs (>= 32 chars of pure base64 without spaces)
    text = re.sub(r"\b[A-Za-z0-9+/]{32,}={0,2}\b", "[REDACTED_BASE64]", text)
    return text


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_event(
    repo_root: Path,
    cycle_id: str,
    node: str,
    event_type: str,
    exit_code: int = 0,
    paths_affected: list = None,
    attempt_id: str = None,
    stdout_text: str = "",
    stderr_text: str = ""
) -> dict:
    traces_dir = repo_root / ".agent" / "learning" / "traces"
    manifest_file = traces_dir / "cycle_manifests.jsonl"
    raw_dir = traces_dir / "raw" / cycle_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)

    # Ensure .gitignore in raw/
    gitignore_path = traces_dir / "raw" / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("*\n!.gitignore\n", encoding="utf-8")

    event_id = f"evt-{uuid.uuid4().hex[:8]}-{int(time.time())}"

    # Save raw stdout/stderr with scrubbing
    stdout_sha = _sha256_text(stdout_text)
    stderr_sha = _sha256_text(stderr_text)

    if stdout_text:
        scrubbed_out = scrub_secrets(stdout_text)
        (raw_dir / f"{event_id}_stdout.log").write_text(scrubbed_out, encoding="utf-8")

    if stderr_text:
        scrubbed_err = scrub_secrets(stderr_text)
        (raw_dir / f"{event_id}_stderr.log").write_text(scrubbed_err, encoding="utf-8")

    # Read previous events to find seq and previous_event_hash
    event_seq = 1
    previous_event_hash = GENESIS_PREV_HASH

    if manifest_file.exists():
        lines = [l.strip() for l in manifest_file.read_text(encoding="utf-8").split("\n") if l.strip()]
        if lines:
            event_seq = len(lines) + 1
            last_event = json.loads(lines[-1])
            previous_event_hash = last_event.get("event_hash", GENESIS_PREV_HASH)

    event_payload = {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id,
        "event_seq": event_seq,
        "event_type": event_type,
        "cycle_id": cycle_id,
        "attempt_id": attempt_id,
        "timestamp": _now(),
        "node": node,
        "exit_code": int(exit_code),
        "paths_affected": paths_affected or [],
        "stdout_sha256": stdout_sha,
        "stderr_sha256": stderr_sha,
        "previous_event_hash": previous_event_hash
    }

    # Hash chaining: SHA256(previous_event_hash + canonical_event_json)
    canonical_json = json.dumps(event_payload, sort_keys=True)
    event_hash = hashlib.sha256(f"{previous_event_hash}{canonical_json}".encode("utf-8")).hexdigest()
    event_payload["event_hash"] = event_hash

    # Append to JSONL
    with open(manifest_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_payload) + "\n")

    return event_payload


def main():
    parser = argparse.ArgumentParser(description="Record Evolution Trace Event")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_app = subparsers.add_parser("append")
    p_app.add_argument("--cycle-id", required=True)
    p_app.add_argument("--node", choices=CANONICAL_NODES, required=True)
    p_app.add_argument("--event-type", choices=EVENT_TYPES, required=True)
    p_app.add_argument("--exit-code", type=int, default=0)
    p_app.add_argument("--paths-affected", default="")
    p_app.add_argument("--attempt-id", default=None)
    p_app.add_argument("--stdout-text", default="")
    p_app.add_argument("--stdout-file", default=None)
    p_app.add_argument("--stderr-text", default="")
    p_app.add_argument("--stderr-file", default=None)
    p_app.add_argument("--repo-dir", type=Path, default=None)

    args = parser.parse_args()

    repo_root = _get_repo_root(args.repo_dir)

    stdout_content = args.stdout_text
    if args.stdout_file:
        f = Path(args.stdout_file)
        if f.exists():
            stdout_content = f.read_text(encoding="utf-8")

    stderr_content = args.stderr_text
    if args.stderr_file:
        f = Path(args.stderr_file)
        if f.exists():
            stderr_content = f.read_text(encoding="utf-8")

    paths = [p.strip() for p in args.paths_affected.split(",") if p.strip()]

    ev = append_event(
        repo_root=repo_root,
        cycle_id=args.cycle_id,
        node=args.node,
        event_type=args.event_type,
        exit_code=args.exit_code,
        paths_affected=paths,
        attempt_id=args.attempt_id,
        stdout_text=stdout_content,
        stderr_text=stderr_content
    )
    print(json.dumps(ev, indent=2))


if __name__ == "__main__":
    main()
