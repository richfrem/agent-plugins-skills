#!/usr/bin/env python
"""
verify_evolution_receipt.py — Programmatic Evolution Integrity Receipts
========================================================================

Purpose:
    Generates and verifies cycle-bound cryptographic Evolution Integrity Receipts.
    Binds the staged git tree, canonical transaction manifest, ordered audit trace,
    verifier exit code, and initial git head:
        cycle_hash = SHA256(canonical_manifest + ordered_events_digest + verifier_exit_code + initial_head + tree_sha)
        Receipt Display = "EVO-INTEGRITY-" + cycle_id[-8:] + "-" + cycle_hash[:12]

Key Input Dependencies:
    - Staged git tree, .agent/learning/traces/cycle_manifests.jsonl
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def _get_repo_root(repo_dir: Path = None) -> Path:
    """Resolve the repo root, defaulting to the git toplevel of the cwd."""
    if repo_dir:
        return repo_dir.resolve()
    try:
        res = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(res.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


def _compute_ordered_events_digest(manifest_file: Path, cycle_id: str) -> tuple[str, list]:
    """Return a digest of the cycle's ordered trace events for receipt binding."""
    if not manifest_file.exists():
        return "", []

    events = []
    for line in manifest_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if ev.get("cycle_id") == cycle_id:
                events.append(ev)
        except Exception:
            pass

    if not events:
        return "", []

    # Sort deterministically by event_seq
    events.sort(key=lambda x: x.get("event_seq", 0))
    # Digest of all event_hashes
    h = hashlib.sha256()
    for ev in events:
        ev_hash = ev.get("event_hash", "")
        canonical_json = json.dumps({k: v for k, v in ev.items() if k != "event_hash"}, sort_keys=True)
        prev_hash = ev.get("previous_event_hash", "")
        expected_hash = hashlib.sha256(f"{prev_hash}{canonical_json}".encode("utf-8")).hexdigest()
        if ev_hash != expected_hash:
            print(f"SECURITY ALERT: Event {ev.get('event_id')} hash mismatch! Tampering detected.", file=sys.stderr)
            sys.exit(1)
        h.update(ev_hash.encode("utf-8"))
    return h.hexdigest(), events


def _get_staged_tree_sha(repo_root: Path) -> str:
    """Return the SHA of the currently staged git tree."""
    try:
        res = subprocess.run(["git", "write-tree"], cwd=repo_root, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "0000000000000000000000000000000000000000"


def compute_receipt(repo_root: Path, cycle_id: str, tree_sha: str = None) -> dict:
    """Compute the EVO-INTEGRITY receipt hash binding tree, trace, and verifier exit code."""
    state_file = repo_root / ".agent" / "learning" / "evolution_state.json"
    manifest_file = repo_root / ".agent" / "learning" / "traces" / "cycle_manifests.jsonl"

    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    ordered_digest, events = _compute_ordered_events_digest(manifest_file, cycle_id)
    if not events:
        print(f"Error: No events found in trace manifest for cycle {cycle_id}", file=sys.stderr)
        sys.exit(1)

    canonical_manifest = json.dumps(state.get("transaction_manifest", {}), sort_keys=True)
    verifier_exit_code = str(state.get("last_verification_exit_code", 0))
    initial_head = state.get("initial_git_head", "0" * 40)
    actual_tree_sha = tree_sha or _get_staged_tree_sha(repo_root)

    preimage = f"{canonical_manifest}|{ordered_digest}|{verifier_exit_code}|{initial_head}|{actual_tree_sha}"
    cycle_hash = hashlib.sha256(preimage.encode("utf-8")).hexdigest()

    cid_suffix = cycle_id[-8:] if len(cycle_id) >= 8 else cycle_id
    receipt_token = f"EVO-INTEGRITY-{cid_suffix}-{cycle_hash[:12]}"

    return {
        "cycle_id": cycle_id,
        "receipt_token": receipt_token,
        "full_hash": cycle_hash,
        "tree_sha": actual_tree_sha,
        "events_count": len(events),
        "preimage_digest": hashlib.sha256(preimage.encode("utf-8")).hexdigest()
    }


def check_asymmetric_persistence(repo_root: Path):
    """Asserts code is clean while wiki/references may be modified."""
    res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]

    code_modifications = []
    allowed_prefixes = ("wiki/", "references/", ".agent/learning/")

    for l in lines:
        path_str = l[3:].strip()
        # If renamed "orig -> new", take new
        if " -> " in path_str:
            path_str = path_str.split(" -> ")[1].strip()

        if not any(path_str.startswith(prefix) for prefix in allowed_prefixes):
            code_modifications.append(path_str)

    if code_modifications:
        print(f"Asymmetric persistence violation: uncommitted code modifications found: {code_modifications}", file=sys.stderr)
        sys.exit(1)

    print("Asymmetric persistence verified: Code is clean; only knowledge/wiki artifacts modified.")
    sys.exit(0)


def main():
    """CLI entry point: compute or verify an evolution integrity receipt."""
    parser = argparse.ArgumentParser(description="Evolution Integrity Receipt Generator & Verifier")
    parser.add_argument("--stage", choices=["pre-commit", "final"], default="pre-commit")
    parser.add_argument("--cycle-id", default=None)
    parser.add_argument("--tree-sha", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--check-asymmetric", action="store_true")
    parser.add_argument("--repo-dir", type=Path, default=None)

    args = parser.parse_args()
    repo_root = _get_repo_root(args.repo_dir)

    if args.check_asymmetric:
        check_asymmetric_persistence(repo_root)

    cycle_id = args.cycle_id
    state_file = repo_root / ".agent" / "learning" / "evolution_state.json"
    if not cycle_id and state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            cycle_id = state.get("cycle_id")
        except Exception:
            pass

    if not cycle_id:
        print("Error: --cycle-id is required or state file must be present", file=sys.stderr)
        sys.exit(1)

    receipt_info = compute_receipt(repo_root, cycle_id, args.tree_sha)

    # Verification mode if --token provided
    if args.token:
        if args.token != receipt_info["receipt_token"]:
            print(f"Receipt verification failed: Tampering detected! Expected {args.token}, computed {receipt_info['receipt_token']}", file=sys.stderr)
            sys.exit(1)
        print("Receipt token verified successfully.")
        return

    # Update state file
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            if args.stage == "pre-commit":
                state["pre_commit_receipt_token"] = receipt_info["receipt_token"]
            else:
                state["final_receipt_token"] = receipt_info["receipt_token"]
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception:
            pass

    print(json.dumps(receipt_info, indent=2))


if __name__ == "__main__":
    main()
