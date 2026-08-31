#!/usr/bin/env python
"""
evolution_state.py — Deterministic Controller for Graph-Planned Evolution
========================================================================

Purpose:
    Single authorized controller and state manager for autonomous self-evolution
    cycles in the Agentic OS. Enforces the 6-Node Graph State Machine DAG,
    advisory directory spinlocks, verifier sovereignty guards, pre-commit receipt
    gating, and Layer 2 asymmetric persistence worktree transfers.

Layer: OS Kernel / Evolution Controller

CLI Subcommands:
    init, plan, authorize, transition, record-verification, set-receipt,
    export-layer2, recover, status
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.1.0"
MAX_ATTEMPTS = 3

DEFAULT_PROTECTED_SET = [
    "evaluate.py",
    "eval_runner.py",
    "plugins/agent-agentic-os/scripts/evaluate.py",
    "plugins/agent-agentic-os/scripts/eval_runner.py",
    ".agent/rules/self-evolution-policy.md",
    ".agent/rules/graph-planning-superpowers-policy.md",
    "plugins/agent-agentic-os/rules/self-evolution-policy.md",
    "plugins/dev-utils/rules/graph-planning-superpowers-policy.md",
]

CANONICAL_NODES = [
    "TRIAGE", "PLAN", "AWAITING_APPROVAL", "AUTHORIZED", "CREATE_WORKTREE",
    "EXECUTE", "VERIFY_GATE", "PRE_COMMIT_RECEIPT", "COMMIT", "ROLLBACK",
    "FINAL_RECEIPT", "COMPLETED", "ESCALATED", "RECOVERY_REQUIRED"
]

STATUS_ENUMS = [
    "IN_PROGRESS", "AWAITING_APPROVAL", "COMMITTED", "ROLLED_BACK",
    "ESCALATED", "RECOVERY_REQUIRED"
]

VALID_DAG = {
    "TRIAGE": ["PLAN", "ESCALATED"],
    "PLAN": ["AWAITING_APPROVAL", "ESCALATED"],
    "AWAITING_APPROVAL": ["AUTHORIZED", "ESCALATED"],
    "AUTHORIZED": ["CREATE_WORKTREE", "ESCALATED"],
    "CREATE_WORKTREE": ["EXECUTE", "ESCALATED"],
    "EXECUTE": ["VERIFY_GATE", "ESCALATED"],
    "VERIFY_GATE": ["PRE_COMMIT_RECEIPT", "PLAN", "ROLLBACK", "ESCALATED"],
    "PRE_COMMIT_RECEIPT": ["COMMIT", "ESCALATED"],
    "COMMIT": ["FINAL_RECEIPT", "ESCALATED"],
    "ROLLBACK": ["FINAL_RECEIPT", "ESCALATED"],
    "FINAL_RECEIPT": ["COMPLETED", "ESCALATED"],
    "COMPLETED": [],
    "ESCALATED": [],
    "RECOVERY_REQUIRED": ["TRIAGE"]
}


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


def _get_git_head(repo_root: Path) -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "0000000000000000000000000000000000000000"


def _state_file_path(repo_root: Path) -> Path:
    return repo_root / ".agent" / "learning" / "evolution_state.json"


def _lock_dir_path(repo_root: Path) -> Path:
    return repo_root / ".agent" / "learning" / "evolution.lock"


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True


def _acquire_lock(repo_root: Path, timeout: int = 2, ttl: int = 1800) -> bool:
    lock_dir = _lock_dir_path(repo_root)
    lock_dir.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout

    while time.time() <= deadline:
        try:
            os.mkdir(lock_dir)
            meta = {
                "pid": os.getpid(),
                "acquired_at": _now(),
                "expires_at": time.time() + ttl,
                "ttl": ttl
            }
            (lock_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
            return True
        except FileExistsError:
            # Check staleness
            meta_file = lock_dir / "meta.json"
            is_stale = False
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    if not _pid_alive(meta.get("pid", 0)) or meta.get("expires_at", 0) < time.time():
                        is_stale = True
                except Exception:
                    is_stale = True
            else:
                is_stale = True

            if is_stale:
                try:
                    for item in lock_dir.iterdir():
                        item.unlink()
                    os.rmdir(lock_dir)
                    continue
                except OSError:
                    pass
            time.sleep(0.05)
    return False


def _release_lock(repo_root: Path):
    lock_dir = _lock_dir_path(repo_root)
    if lock_dir.exists():
        try:
            for item in lock_dir.iterdir():
                item.unlink()
            os.rmdir(lock_dir)
        except OSError:
            pass


def _atomic_write_json(file_path: Path, data: dict):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=file_path.parent, delete=False, mode="w", encoding="utf-8") as tf:
        json.dump(data, tf, indent=2)
        tf.flush()
        os.fsync(tf.fileno())
        temp_name = tf.name
    os.replace(temp_name, file_path)


def _load_state(repo_root: Path) -> dict:
    p = _state_file_path(repo_root)
    if not p.exists():
        print(f"Error: Evolution state file not found at {p}", file=sys.stderr)
        sys.exit(1)
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _file_hash(p: Path) -> str:
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _check_verifier_sovereignty(repo_root: Path, state: dict):
    # 1. Check default baseline hashes
    default_baseline = state.get("default_baseline_hashes", {})
    for p_str, expected_hash in default_baseline.items():
        curr_hash = _file_hash(repo_root / p_str)
        if expected_hash and curr_hash != expected_hash:
            print(f"SECURITY ALERT: Verifier sovereignty violation! Protected baseline file {p_str} modified.", file=sys.stderr)
            sys.exit(2)

    # 2. Check manifest-declared verifier files
    manifest = state.get("transaction_manifest", {})
    verifier_files = manifest.get("verifier_files", [])
    recorded_hashes = manifest.get("verifier_hashes", {})
    
    for v_rel in verifier_files:
        v_path = repo_root / v_rel
        curr_hash = _file_hash(v_path)
        expected_hash = recorded_hashes.get(v_rel)
        if expected_hash and curr_hash != expected_hash:
            print(f"SECURITY ALERT: Verifier sovereignty violation! {v_rel} modified.", file=sys.stderr)
            sys.exit(2)


# ============================================================================
# Command Handlers
# ============================================================================

def cmd_init(args):
    repo_root = _get_repo_root(args.repo_dir)

    # Check if a cycle is already active in evolution_state.json
    state_file = _state_file_path(repo_root)
    if state_file.exists():
        try:
            existing_state = json.loads(state_file.read_text(encoding="utf-8"))
            if existing_state.get("status") == "IN_PROGRESS":
                print(f"Error: An evolution cycle is already in progress (lock held): {existing_state.get('cycle_id')}", file=sys.stderr)
                sys.exit(1)
        except Exception:
            pass

    if not _acquire_lock(repo_root):
        print(f"Error: Could not acquire lock at {_lock_dir_path(repo_root)} (another process active)", file=sys.stderr)
        sys.exit(1)

    initial_head = _get_git_head(repo_root)
    
    # Record baseline hashes for DEFAULT_PROTECTED_SET
    default_baseline = {}
    for p_str in DEFAULT_PROTECTED_SET:
        p = repo_root / p_str
        if p.exists():
            default_baseline[p_str] = _file_hash(p)

    state = {
        "schema_version": SCHEMA_VERSION,
        "cycle_id": args.cycle_id,
        "lock_pid": os.getpid(),
        "current_node": "TRIAGE",
        "status": "IN_PROGRESS",
        "attempt_count": 0,
        "max_attempts": MAX_ATTEMPTS,
        "tier": args.tier,
        "initial_git_head": initial_head,
        "worktree_path": None,
        "authorization": {
            "status": "PENDING",
            "cycle_id": args.cycle_id,
            "plan_hash_sha256": None,
            "transaction_manifest_hash_sha256": None,
            "verifier_identity_sha256": None,
            "authorized_operations": [],
            "authorized_at": None
        },
        "default_baseline_hashes": default_baseline,
        "transaction_manifest": {},
        "baseline_untracked_files": [],
        "owned_tracked_files": [],
        "owned_untracked_files": [],
        "wiki_files": [],
        "event_ids": [],
        "last_verification_exit_code": None,
        "verification_provenance": None,
        "pre_commit_receipt_token": None,
        "final_receipt_token": None
    }
    _atomic_write_json(_state_file_path(repo_root), state)
    print(f"Initialized evolution cycle {args.cycle_id} in TRIAGE mode.")


def cmd_plan(args):
    repo_root = _get_repo_root(args.repo_dir)
    state = _load_state(repo_root)
    
    manifest_data = {}
    if args.manifest:
        p = Path(args.manifest).resolve()
        if p.exists():
            manifest_data = json.loads(p.read_text(encoding="utf-8"))
    
    # Calculate verifier hashes (manifest files + default protected files)
    verifier_files = list(manifest_data.get("verifier_files", []))
    for p_str in DEFAULT_PROTECTED_SET:
        if (repo_root / p_str).exists() and p_str not in verifier_files:
            verifier_files.append(p_str)
    manifest_data["verifier_files"] = verifier_files

    verifier_hashes = {}
    for vf in verifier_files:
        v_path = repo_root / vf
        if v_path.exists():
            verifier_hashes[vf] = _file_hash(v_path)
    manifest_data["verifier_hashes"] = verifier_hashes

    # Re-plan invalidates authorization on manifest hash mismatch
    manifest_json = json.dumps(manifest_data, sort_keys=True)
    new_manifest_hash = hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()
    auth = state.get("authorization", {})
    if auth.get("status") == "GRANTED":
        if auth.get("transaction_manifest_hash_sha256") != new_manifest_hash:
            auth["status"] = "INVALIDATED"
            state["authorization"] = auth

    state["transaction_manifest"] = manifest_data
    state["current_node"] = "PLAN"
    _atomic_write_json(_state_file_path(repo_root), state)
    print("Plan and transaction manifest recorded.")


def cmd_authorize(args):
    repo_root = _get_repo_root(args.repo_dir)
    state = _load_state(repo_root)
    
    if state["cycle_id"] != args.cycle_id:
        print(f"Error: cycle_id mismatch: expected {state['cycle_id']}, got {args.cycle_id}", file=sys.stderr)
        sys.exit(1)

    ops = [op.strip() for op in args.operations.split(",") if op.strip()]
    state["authorization"] = {
        "status": "GRANTED",
        "cycle_id": args.cycle_id,
        "plan_hash_sha256": args.plan_hash,
        "transaction_manifest_hash_sha256": hashlib.sha256(json.dumps(state.get("transaction_manifest", {}), sort_keys=True).encode("utf-8")).hexdigest(),
        "verifier_identity_sha256": None,
        "authorized_operations": ops,
        "authorized_at": _now()
    }
    state["current_node"] = "AUTHORIZED"
    _atomic_write_json(_state_file_path(repo_root), state)
    print(f"Cycle {args.cycle_id} authorized with operations: {ops}")


def cmd_transition(args):
    repo_root = _get_repo_root(args.repo_dir)
    state = _load_state(repo_root)
    target_node = args.to

    if target_node not in CANONICAL_NODES:
        print(f"Error: Unknown node {target_node}", file=sys.stderr)
        sys.exit(1)

    current_node = state.get("current_node", "TRIAGE")
    valid_targets = VALID_DAG.get(current_node, [])

    if target_node not in valid_targets:
        print(f"Illegal transition from {current_node} to {target_node}", file=sys.stderr)
        sys.exit(1)

    # Machine-enforced attempt ceiling: Cannot loop back to PLAN if attempt_count >= MAX_ATTEMPTS
    if target_node == "PLAN" and current_node == "VERIFY_GATE":
        if state.get("attempt_count", 0) >= MAX_ATTEMPTS:
            print(f"Error: Attempt ceiling reached ({MAX_ATTEMPTS} attempts max). Cannot transition to PLAN; must ROLLBACK.", file=sys.stderr)
            sys.exit(1)

    # Proposal Mode Guard: Cannot transition to CREATE_WORKTREE without GRANTED authorization
    if target_node == "CREATE_WORKTREE":
        if state.get("authorization", {}).get("status") != "GRANTED":
            print(f"Authorization required: Cannot transition to CREATE_WORKTREE without explicit user authorization (status={state.get('authorization', {}).get('status')}).", file=sys.stderr)
            sys.exit(1)
        _check_verifier_sovereignty(repo_root, state)
        # Persist where the caller's `git worktree add` actually put the sandbox, so `verify`
        # (and any future commit step) execute against the mutated copy, not the main checkout.
        # Existence is not required here -- the caller may create the worktree immediately after
        # this transition returns.
        worktree_path = getattr(args, "worktree_path", None)
        if worktree_path is not None:
            state["worktree_path"] = str(Path(worktree_path).resolve())

    # Verifier Sovereignty Guard on EXECUTE
    if target_node == "EXECUTE":
        _check_verifier_sovereignty(repo_root, state)
        state["attempt_count"] = state.get("attempt_count", 0) + 1

    # Transition to PRE_COMMIT_RECEIPT: Must have executed verifier with exit code 0 and controller provenance
    if target_node == "PRE_COMMIT_RECEIPT":
        _check_verifier_sovereignty(repo_root, state)
        prov = state.get("verification_provenance")
        if (not isinstance(prov, dict)
                or prov.get("source") != "controller"
                or prov.get("attempt") != state.get("attempt_count")
                or prov.get("exit_code") != 0):
            print(
                "Verification gate violation: no controller-executed PASS for the current attempt. "
                "Self-reported exit codes cannot drive PRE_COMMIT_RECEIPT.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Pre-Commit Receipt Guard: Cannot transition to COMMIT without token and commit permission
    if target_node == "COMMIT":
        auth_ops = state.get("authorization", {}).get("authorized_operations", [])
        if "commit" not in auth_ops:
            print("Authorization violation: 'commit' is not in authorized_operations.", file=sys.stderr)
            sys.exit(1)
        token = state.get("pre_commit_receipt_token")
        if not token:
            print("Integrity gate violation: pre_commit_receipt_token is required before transition to COMMIT.", file=sys.stderr)
            sys.exit(1)

        # Cryptographic re-verification against git write-tree and event chain.
        # Must recompute the staged tree in the same directory the pre-commit token was
        # generated against (the worktree, when one is recorded) -- otherwise this always
        # mismatches for any cycle that mutates inside an isolated worktree.
        script_dir = Path(__file__).resolve().parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        try:
            import verify_evolution_receipt
            tree_exec_dir = repo_root
            if state.get("worktree_path") and Path(state["worktree_path"]).exists():
                tree_exec_dir = Path(state["worktree_path"])
            recompute_tree_sha = subprocess.run(
                ["git", "write-tree"], cwd=tree_exec_dir, capture_output=True, text=True
            ).stdout.strip()
            actual = verify_evolution_receipt.compute_receipt(repo_root, state["cycle_id"], tree_sha=recompute_tree_sha)
            if token != actual.get("receipt_token"):
                print(f"Integrity gate violation: pre_commit_receipt_token mismatch! Stored: {token}, Recomputed: {actual.get('receipt_token')}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Integrity gate violation: Receipt cryptographic verification error: {e}", file=sys.stderr)
            sys.exit(1)

    state["current_node"] = target_node
    if target_node == "AWAITING_APPROVAL":
        state["status"] = "AWAITING_APPROVAL"
    elif target_node == "COMPLETED":
        state["status"] = "COMMITTED"
        _release_lock(repo_root)
    elif target_node == "ESCALATED":
        state["status"] = "ESCALATED"
        _release_lock(repo_root)
    elif target_node == "ROLLBACK":
        state["status"] = "ROLLED_BACK"

    _atomic_write_json(_state_file_path(repo_root), state)
    print(f"Transitioned to node: {target_node}")


def cmd_verify(args):
    repo_root = _get_repo_root(args.repo_dir)
    state = _load_state(repo_root)
    _check_verifier_sovereignty(repo_root, state)

    manifest = state.get("transaction_manifest", {})
    verifier_argv = manifest.get("verifier_argv", [])
    if not verifier_argv:
        print("Error: No verifier_argv declared in transaction_manifest", file=sys.stderr)
        sys.exit(1)

    exec_dir = repo_root
    if state.get("worktree_path"):
        wt = Path(state["worktree_path"])
        if not wt.exists():
            print(f"Verify error: worktree_path {wt} does not exist", file=sys.stderr)
            sys.exit(1)
        exec_dir = wt

    print(f"Controller executing verifier: {verifier_argv} in {exec_dir}")
    res = subprocess.run(verifier_argv, cwd=exec_dir, capture_output=True, text=True)
    exit_code = res.returncode
    state["last_verification_exit_code"] = exit_code

    # V1: stamp controller-owned provenance. Only `verify` may write this block.
    state["verification_provenance"] = {
        "source": "controller",
        "attempt": state.get("attempt_count", 0),
        "exit_code": exit_code,
        "verifier_argv_sha256": hashlib.sha256(
            json.dumps(verifier_argv, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "at": _now(),
    }

    # Check sovereignty after execution
    _check_verifier_sovereignty(repo_root, state)

    _atomic_write_json(_state_file_path(repo_root), state)
    print(f"Controller executed verifier: exit code: {exit_code}")
    if exit_code != 0:
        if res.stdout:
            print(f"Verifier stdout: {res.stdout[:500]}", file=sys.stderr)
        if res.stderr:
            print(f"Verifier stderr: {res.stderr[:500]}", file=sys.stderr)
        sys.exit(exit_code)


def cmd_record_verification(args):
    # V1: NON-AUTHORITATIVE. Retained only so old call sites do not hard-crash.
    # It MUST NOT write last_verification_exit_code or verification_provenance.
    # Only `verify` (controller-executed) can drive VERIFY_GATE -> PRE_COMMIT_RECEIPT.
    print(
        "Warning: 'record-verification' is non-authoritative and cannot drive the gate. "
        "Use 'verify' so the controller executes the declared verifier itself.",
        file=sys.stderr,
    )
    sys.exit(0)


def cmd_set_receipt(args):
    repo_root = _get_repo_root(args.repo_dir)
    state = _load_state(repo_root)
    if args.stage == "pre-commit":
        state["pre_commit_receipt_token"] = args.token
    elif args.stage == "final":
        state["final_receipt_token"] = args.token
    _atomic_write_json(_state_file_path(repo_root), state)
    print(f"Receipt token set for stage '{args.stage}': {args.token}")


def _copy_layer2(from_wt: Path, dest: Path):
    # wiki/
    wt_wiki = from_wt / "wiki"
    if wt_wiki.exists():
        dest_wiki = dest / "wiki"
        dest_wiki.mkdir(parents=True, exist_ok=True)
        for root, _, files in os.walk(wt_wiki):
            rel_root = Path(root).relative_to(wt_wiki)
            target_dir = dest_wiki / rel_root
            target_dir.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(Path(root) / f, target_dir / f)
    # map-debt.md and evolution-log.md, wherever they live in the worktree
    for ref_name in ["map-debt.md", "evolution-log.md"]:
        for cand in from_wt.glob(f"**/{ref_name}"):
            rel_path = cand.relative_to(from_wt)
            target_file = dest / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cand, target_file)


def cmd_export_layer2(args):
    from_wt = Path(args.from_worktree).resolve()
    to_main = Path(args.to_main).resolve()
    if not from_wt.exists():
        print(f"Error: Worktree path {from_wt} does not exist", file=sys.stderr)
        sys.exit(1)

    if not getattr(args, "commit_knowledge", False):
        # Legacy preview / non-git use: working-tree copy only, no commit.
        _copy_layer2(from_wt, to_main)
        print("Layer 2 artifacts copied to main checkout (working-tree only, no commit).")
        return

    # V2: durable persistence WITHOUT committing to main.
    cycle_id = args.cycle_id
    if not cycle_id:
        state_file = _state_file_path(to_main)
        if state_file.exists():
            try:
                cycle_id = json.loads(state_file.read_text(encoding="utf-8")).get("cycle_id")
            except Exception:
                cycle_id = None
    if not cycle_id:
        print("Error: --cycle-id required for --commit-knowledge", file=sys.stderr)
        sys.exit(1)

    branch = f"knowledge/{cycle_id}"
    kt = to_main.parent / f"knowledge-wt-{cycle_id}"

    # Create a dedicated branch + isolated worktree at current HEAD.
    res = subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(kt), "HEAD"],
        cwd=to_main, capture_output=True, text=True,
    )
    if res.returncode != 0:
        print(f"Error: could not create knowledge worktree/branch: {res.stderr}", file=sys.stderr)
        sys.exit(1)
    try:
        _copy_layer2(from_wt, kt)
        subprocess.run(["git", "add", "-A"], cwd=kt, check=True, capture_output=True)
        st = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=kt,
                            capture_output=True, text=True)
        if not st.stdout.strip():
            print("Warning: no Layer 2 artifacts to commit.", file=sys.stderr)
        else:
            subprocess.run(
                ["git", "commit", "-m",
                 f"knowledge({cycle_id}): persist Layer 2 evolution insights [skip ci]"],
                cwd=kt, check=True, capture_output=True,
            )
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(kt)],
                       cwd=to_main, capture_output=True)
    print(f"Layer 2 committed to branch '{branch}'. Main working tree and HEAD untouched.")


def cmd_recover(args):
    repo_root = _get_repo_root(args.repo_dir)
    state_file = _state_file_path(repo_root)
    if not state_file.exists():
        print("No evolution state to recover.", file=sys.stderr)
        sys.exit(0)

    state = _load_state(repo_root)

    # Check git status for uncommitted/unrecorded changes
    git_status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    dirty_lines = [l.strip() for l in git_status.stdout.split("\n") if l.strip()]

    # Filter out internal .agent/ state files
    untracked_unknown = False
    for l in dirty_lines:
        path_str = l[3:].strip()
        if not (path_str.startswith(".agent/") or path_str == ".agent" or path_str.startswith(".agent")):
            untracked_unknown = True
            break

    if untracked_unknown:
        state["current_node"] = "RECOVERY_REQUIRED"
        state["status"] = "RECOVERY_REQUIRED"
        _atomic_write_json(state_file, state)
        print("Ambiguous or dirty git state detected during recovery: Set to RECOVERY_REQUIRED.")
        return

    # Check traces
    traces_file = repo_root / ".agent" / "learning" / "traces" / "cycle_manifests.jsonl"
    events = []
    if traces_file.exists():
        for l in traces_file.read_text(encoding="utf-8").strip().split("\n"):
            if l.strip():
                try:
                    events.append(json.loads(l))
                except Exception:
                    pass

    event_types = [e.get("event_type") for e in events]
    if "mutation.completed" in event_types:
        state["current_node"] = "VERIFY_GATE"
        state["status"] = "IN_PROGRESS"
        _atomic_write_json(state_file, state)
        print("Recovered to VERIFY_GATE.")
    else:
        state["current_node"] = "TRIAGE"
        state["status"] = "IN_PROGRESS"
        _atomic_write_json(state_file, state)
        print("Recovered cleanly to TRIAGE.")


def cmd_status(args):
    repo_root = _get_repo_root(args.repo_dir)
    state = _load_state(repo_root)
    print(json.dumps(state, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Evolution State Controller")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init")
    p_init.add_argument("--cycle-id", required=True)
    p_init.add_argument("--tier", default="Tier 2")
    p_init.add_argument("--repo-dir", type=Path, default=None)

    # plan
    p_plan = subparsers.add_parser("plan")
    p_plan.add_argument("--manifest", default=None)
    p_plan.add_argument("--repo-dir", type=Path, default=None)

    # authorize
    p_auth = subparsers.add_parser("authorize")
    p_auth.add_argument("--cycle-id", required=True)
    p_auth.add_argument("--plan-hash", default=None)
    p_auth.add_argument("--operations", default="create_worktree,mutate,verify,write_layer2,commit")
    p_auth.add_argument("--repo-dir", type=Path, default=None)

    # transition
    p_trans = subparsers.add_parser("transition")
    p_trans.add_argument("--to", required=True)
    p_trans.add_argument("--repo-dir", type=Path, default=None)
    p_trans.add_argument("--worktree-path", type=Path, default=None)

    # verify
    p_ver = subparsers.add_parser("verify")
    p_ver.add_argument("--repo-dir", type=Path, default=None)

    # record-verification
    p_rec = subparsers.add_parser("record-verification")
    p_rec.add_argument("--exit-code", type=int, required=True)
    p_rec.add_argument("--repo-dir", type=Path, default=None)

    # set-receipt
    p_recp = subparsers.add_parser("set-receipt")
    p_recp.add_argument("--stage", choices=["pre-commit", "final"], required=True)
    p_recp.add_argument("--token", required=True)
    p_recp.add_argument("--repo-dir", type=Path, default=None)

    # export-layer2
    p_exp = subparsers.add_parser("export-layer2")
    p_exp.add_argument("--from-worktree", required=True)
    p_exp.add_argument("--to-main", required=True)
    p_exp.add_argument("--cycle-id", default=None)
    p_exp.add_argument("--commit-knowledge", action="store_true", default=False)

    # recover
    p_recov = subparsers.add_parser("recover")
    p_recov.add_argument("--repo-dir", type=Path, default=None)

    # status
    p_stat = subparsers.add_parser("status")
    p_stat.add_argument("--repo-dir", type=Path, default=None)

    args = parser.parse_args()

    dispatch = {
        "init": cmd_init,
        "plan": cmd_plan,
        "authorize": cmd_authorize,
        "transition": cmd_transition,
        "verify": cmd_verify,
        "record-verification": cmd_record_verification,
        "set-receipt": cmd_set_receipt,
        "export-layer2": cmd_export_layer2,
        "recover": cmd_recover,
        "status": cmd_status
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
