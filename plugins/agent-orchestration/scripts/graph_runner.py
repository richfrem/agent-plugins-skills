#!/usr/bin/env python3
"""
Graph Runner for Agent Orchestration
====================================

Deterministic executor for compiled graph-manifest.json files.
Features:
- Integrated manifest validation at startup
- Manifest SHA256 integrity binding (--expect-manifest-sha256)
- Workspace confinement (--worktree, --create-worktree, --no-workspace)
- Approval gates (--approval none | prompt) with fail-closed non-interactive prompt
- Strict null-byte delimited git status parsing for mutation_targets and forbidden_paths
- Non-mutation node immutability enforcement (HEAD and porcelain check)
- Verifier integrity (verifier_hash checks)
- Main-thread rollback after thread pool drain
- Append-only receipts (.graph-run/<graph_id>/<run_id>/receipts.jsonl) anchored outside worktree
- Pure Python standard library (zero external packages)
"""

import sys
import os
import json
import argparse
import subprocess
import signal
import hashlib
import fnmatch
import shutil
import datetime
import uuid
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure script dir in sys.path to import validate_manifest
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_manifest import load_schema, validate_schema, validate_graph_topology


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> Tuple[int, str, str]:
    """Execute subprocess with timeout and process group cleanup; return exit_code, stdout, stderr."""
    try:
        kwargs: Dict[str, Any] = {
            "cwd": cwd,
            "env": env or os.environ.copy(),
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
        }
        if os.name == "posix":
            kwargs["start_new_session"] = True

        p = subprocess.Popen(cmd, **kwargs)
        try:
            stdout, stderr = p.communicate(timeout=timeout)
            out_str = stdout if isinstance(stdout, str) else (stdout.decode("utf-8", errors="replace") if stdout else "")
            err_str = stderr if isinstance(stderr, str) else (stderr.decode("utf-8", errors="replace") if stderr else "")
            return p.returncode, out_str, err_str
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass
            else:
                p.kill()
            try:
                out_raw, err_raw = p.communicate(timeout=5)
            except Exception:
                out_raw, err_raw = "", ""
            out_str = out_raw if isinstance(out_raw, str) else (out_raw.decode("utf-8", errors="replace") if out_raw else "")
            err_str = err_raw if isinstance(err_raw, str) else (err_raw.decode("utf-8", errors="replace") if err_raw else "")
            return 124, out_str, f"Execution timed out after {timeout} seconds\n{err_str}"
        except (KeyboardInterrupt, SystemExit, BaseException):
            if os.name == "posix":
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass
            else:
                p.kill()
            raise
    except Exception as e:
        return 1, "", str(e)


def compute_sha256(data: str) -> str:
    """Compute hex SHA256 digest of string data."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_file_sha256(path: Path) -> str:
    """Compute hex SHA256 digest of file content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_git_diff_z(workdir: Path, ref_range: str) -> List[str]:
    """Parse git diff --name-only -z ref_range into list of changed file paths."""
    rc, out, _ = run_cmd(["git", "diff", "--name-only", "-z", ref_range], cwd=workdir)
    if rc != 0 or not out:
        return []
    return [p for p in out.split("\0") if p]


def parse_git_status_z(workdir: Path) -> List[str]:
    """Parse git status --porcelain=v1 -z --untracked-files=all into changed paths."""
    rc, out, _ = run_cmd(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=workdir)
    if rc != 0 or not out:
        return []

    changed_files = []
    # Null-delimited entries
    raw_entries = out.split("\0")
    idx = 0
    while idx < len(raw_entries):
        entry = raw_entries[idx]
        if not entry:
            idx += 1
            continue
        # Format: XY <path>
        status = entry[:2]
        path = entry[3:]  # Exactly after 'XY ' without stripping
        changed_files.append(path)
        # If rename or copy, the next entry is the original path
        if "R" in status or "C" in status:
            idx += 1
            if idx < len(raw_entries) and raw_entries[idx]:
                orig_path = raw_entries[idx]
                changed_files.append(orig_path)
        idx += 1
    return changed_files


class GraphRunner:
    def __init__(self, manifest_path: Path, workdir: Path, approval_mode: str,
                 run_id: Optional[str] = None, run_dir: Optional[Path] = None,
                 expected_manifest_sha: Optional[str] = None,
                 parsed_manifest: Optional[Tuple[Dict[str, Any], bytes]] = None):
        self.manifest_path = manifest_path.resolve()
        if parsed_manifest:
            self.manifest, manifest_bytes = parsed_manifest
            self.manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        else:
            manifest_bytes = self.manifest_path.read_bytes()
            self.manifest = json.loads(manifest_bytes.decode("utf-8"))
            self.manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()

        self.graph_id = self.manifest["graph_id"]
        self.run_id = run_id or f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.workdir = workdir.resolve()
        self.approval_mode = approval_mode
        self.expected_manifest_sha = expected_manifest_sha

        self.budget = self.manifest.get("budget", {})
        self.max_concurrency = self.budget.get("max_parallel_concurrency", 4)
        self.max_retries = self.budget.get("max_retries_per_node", 2)

        self.nodes_list: List[Dict[str, Any]] = self.manifest.get("nodes", [])
        self.nodes: Dict[str, Dict[str, Any]] = {n["id"]: n for n in self.nodes_list}

        # Anchor run directory outside the worktree mutation tree to survive git clean
        if run_dir:
            self.run_dir = run_dir.resolve() / self.graph_id / self.run_id
        else:
            # Default: place in .git/graph-run if git repo, else parent/.graph-run
            git_common = self.find_git_common_dir(self.workdir)
            if git_common:
                self.run_dir = git_common / "graph-run" / self.graph_id / self.run_id
            else:
                self.run_dir = self.workdir.parent / ".graph-run" / self.graph_id / self.run_id

        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_file = self.run_dir / "receipts.jsonl"
        self.state_file = self.run_dir / "state.json"
        self.scratch_base = self.run_dir / "scratch"
        self.scratch_base.mkdir(parents=True, exist_ok=True)

        self.start_sha: Optional[str] = None
        self.is_git_repo = False
        self.completed_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()
        self.has_prompted_mutation = False

        # Identify fallback nodes (only nodes declaring role='fallback')
        self.fallback_nodes: Set[str] = {n["id"] for n in self.nodes_list if n.get("role") == "fallback"}

    def find_git_common_dir(self, directory: Path) -> Optional[Path]:
        """Find the real git directory/common-dir so receipts are not wiped by git clean."""
        rc, out, _ = run_cmd(["git", "rev-parse", "--git-common-dir"], cwd=directory)
        if rc == 0 and out.strip():
            p = Path(out.strip())
            return p if p.is_absolute() else (directory / p).resolve()
        rc, out, _ = run_cmd(["git", "rev-parse", "--git-dir"], cwd=directory)
        if rc == 0 and out.strip():
            p = Path(out.strip())
            return p if p.is_absolute() else (directory / p).resolve()
        return None

    def validate_manifest_integrity(self) -> None:
        """Verify manifest SHA and run structural and topological validation."""
        # 1. Check SHA256 binding
        actual_sha = self.manifest_sha
        if self.expected_manifest_sha:
            if actual_sha != self.expected_manifest_sha:
                raise RuntimeError(
                    f"Manifest SHA256 mismatch: expected '{self.expected_manifest_sha}', got '{actual_sha}'"
                )

        mutations = [n for n in self.nodes_list if n.get("type") == "sequential_mutation"]
        if mutations and self.approval_mode == "none" and not self.expected_manifest_sha:
            raise RuntimeError(
                "Approval invariant: Running a mutation graph with --approval none requires "
                "--expect-manifest-sha256 to cryptographically bind the approved manifest."
            )

        # 2. Structural & Topological validation
        schema = load_schema()
        schema_errs = validate_schema(self.manifest, schema)
        if schema_errs:
            raise RuntimeError("Manifest schema validation failed:\n  " + "\n  ".join(schema_errs))

        topo_errs = validate_graph_topology(self.manifest, check_approval_none=(self.approval_mode == "none"))
        if topo_errs:
            raise RuntimeError("Manifest topology validation failed:\n  " + "\n  ".join(topo_errs))

    def record_receipt(self, node_id: str, attempt: int, exit_code: int, contract_ok: bool,
                       diff_hash: str, commit_sha: Optional[str] = None,
                       stdout_hash: str = "", stderr_hash: str = "") -> None:
        """Append an attempt receipt to receipts.jsonl."""
        entry = {
            "node_id": node_id,
            "attempt": attempt,
            "exit_code": exit_code,
            "contract_ok": contract_ok,
            "diff_hash": diff_hash,
            "commit_sha": commit_sha,
            "stdout_hash": stdout_hash,
            "stderr_hash": stderr_hash,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(self.receipts_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def save_state(self, status: str, error: Optional[str] = None) -> None:
        """Write current runner state to state.json."""
        state = {
            "graph_id": self.graph_id,
            "run_id": self.run_id,
            "status": status,
            "start_sha": self.start_sha,
            "completed_nodes": list(self.completed_nodes),
            "failed_nodes": list(self.failed_nodes),
            "error": error,
            "updated_at": datetime.datetime.now().isoformat()
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def verify_clean_git(self) -> None:
        """Verify worktree exists, is clean, and capture start SHA."""
        rc, out, _ = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.workdir)
        if rc != 0 or out.strip() != "true":
            self.is_git_repo = False
            return

        self.is_git_repo = True
        rc, out, _ = run_cmd(["git", "status", "--porcelain=v1"], cwd=self.workdir)
        if out.strip():
            raise RuntimeError(
                f"Target worktree '{self.workdir}' has uncommitted changes. "
                "Clean working tree is strictly required before starting graph run."
            )

        rc, out, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.workdir)
        if rc == 0:
            self.start_sha = out.strip()

    def get_porcelain_hash(self) -> str:
        """Calculate SHA256 of git status --porcelain, failing closed on git error."""
        if not self.is_git_repo:
            return ""
        rc, out, err = run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=self.workdir)
        if rc != 0:
            raise RuntimeError(f"git status failed with exit code {rc}: {err}")
        return compute_sha256(out)

    def get_current_head(self) -> str:
        """Get current HEAD commit SHA."""
        if not self.is_git_repo:
            return ""
        rc, out, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.workdir)
        if rc != 0:
            raise RuntimeError(f"git rev-parse HEAD failed with exit code {rc}: {err}")
        return out.strip()

    def rollback_and_halt(self, reason: str) -> None:
        """Reset worktree to start SHA and clean untracked files created during run (main thread only)."""
        print(f"\n[TRIGGER] Rollback and halt: {reason}", file=sys.stderr)
        if self.is_git_repo and self.start_sha:
            run_cmd(["git", "reset", "--hard", self.start_sha], cwd=self.workdir)
            run_cmd(["git", "clean", "-fd"], cwd=self.workdir)
            print(f"Worktree rolled back to start commit {self.start_sha[:8]}", file=sys.stderr)
        self.save_state("rolled_back", error=reason)

    def prompt_human(self, prompt_text: str) -> bool:
        """Prompt user for confirmation; fail closed if non-interactive."""
        if not sys.stdin.isatty():
            print(f"Non-interactive stdin detected; rejecting prompt for: {prompt_text}", file=sys.stderr)
            return False
        print(f"\n[APPROVAL PROMPT] {prompt_text} (y/N): ", end="", flush=True)
        try:
            line = sys.stdin.readline().strip().lower()
            return line in ("y", "yes")
        except Exception:
            return False

    def verify_verifier_hash(self, node: Dict[str, Any]) -> None:
        """Check verifier_hash if declared."""
        expected_hash = node.get("verifier_hash")
        if not expected_hash:
            return

        cmd = node.get("command_or_eval", "")
        file_path = self.workdir / cmd.split()[0] if cmd else None
        if file_path and file_path.is_file():
            actual_hash = compute_file_sha256(file_path)
        else:
            actual_hash = compute_sha256(cmd)

        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Verifier hash mismatch for node '{node['id']}': expected {expected_hash}, got {actual_hash}"
            )

    def enforce_mutation_boundaries(self, node: Dict[str, Any], pre_node_head: str) -> None:
        """Verify status and diff only touch mutation_targets and zero forbidden_paths."""
        if not self.is_git_repo:
            return

        status_files = parse_git_status_z(self.workdir)
        diff_files = []
        if pre_node_head:
            diff_files = parse_git_diff_z(self.workdir, f"{pre_node_head}..HEAD")

        all_changed_files = sorted(set(status_files + diff_files))
        mutation_targets = node.get("mutation_targets", [])
        forbidden_paths = node.get("forbidden_paths", [])

        for path in all_changed_files:
            # Check forbidden paths
            for pattern in forbidden_paths:
                if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"*/{pattern}"):
                    raise RuntimeError(f"Mutation node '{node['id']}' modified forbidden path '{path}' (pattern: '{pattern}')")

            # Check mutation targets
            if mutation_targets is not None:
                matched = False
                for target in mutation_targets:
                    if target in ("*", "**"):
                        raise RuntimeError(f"Bare wildcard '{target}' in mutation_targets is prohibited.")
                    if path == target or fnmatch.fnmatch(path, target):
                        matched = True
                        break
                if not matched:
                    raise RuntimeError(f"Mutation node '{node['id']}' modified unauthorized path '{path}' (outside mutation_targets)")

    def execute_node(self, node_id: str) -> bool:
        """Execute a single node with retries and failure escalation (never calls rollback_and_halt)."""
        node = self.nodes[node_id]
        node_type = node.get("type")
        is_mutation = (node_type == "sequential_mutation")
        reversible = node.get("reversible", True)
        timeout = node.get("timeout_seconds", 300)

        # 1. Approval prompt check
        if is_mutation:
            if self.approval_mode == "prompt" and not self.has_prompted_mutation:
                confirmed = self.prompt_human(f"Authorize initial repository mutation (Node '{node_id}')")
                if not confirmed:
                    print(f"[REJECTED] User rejected mutation approval for node '{node_id}'", file=sys.stderr)
                    return False
                self.has_prompted_mutation = True

        if not reversible and self.approval_mode == "prompt":
            confirmed = self.prompt_human(f"Authorize IRREVERSIBLE external action (Node '{node_id}')")
            if not confirmed:
                print(f"[REJECTED] User rejected irreversible node '{node_id}'", file=sys.stderr)
                return False

        # 2. Scratch dir setup
        scratch_dir = self.scratch_base / node_id
        scratch_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["GRAPH_SCRATCH_DIR"] = str(scratch_dir)
        env["GRAPH_NODE_ID"] = node_id
        env["GRAPH_RUN_ID"] = self.run_id

        # 3. Verifier hash pre-check
        try:
            self.verify_verifier_hash(node)
        except Exception as e:
            self.record_receipt(node_id, attempt=1, exit_code=1, contract_ok=False, diff_hash="")
            print(f"[ERROR] Verifier integrity check failed for node '{node_id}': {e}", file=sys.stderr)
            return False

        # Record pre-node state
        pre_node_head = self.get_current_head()
        pre_node_hash = self.get_porcelain_hash()

        # 4. Attempt loop
        attempts = 0
        cmd = node.get("command_or_eval", "")

        while attempts <= self.max_retries:
            attempts += 1
            print(f"[NODE {node_id}] Attempt {attempts}/{self.max_retries + 1}: {cmd}")

            # Reset working tree only for sequential mutation nodes (never for concurrent read nodes)
            if attempts > 1 and is_mutation and self.is_git_repo and pre_node_head:
                run_cmd(["git", "reset", "--hard", pre_node_head], cwd=self.workdir)
                run_cmd(["git", "clean", "-fd"], cwd=self.workdir)

            rc, stdout, stderr = run_cmd(["bash", "-c", cmd], cwd=self.workdir, env=env, timeout=timeout)

            # Persist stdout and stderr logs to scratch
            stdout_path = scratch_dir / f"attempt_{attempts}_stdout.log"
            stderr_path = scratch_dir / f"attempt_{attempts}_stderr.log"
            stdout_path.write_text(stdout, encoding="utf-8")
            stderr_path.write_text(stderr, encoding="utf-8")
            stdout_hash = compute_sha256(stdout)
            stderr_hash = compute_sha256(stderr)

            diff_hash = self.get_porcelain_hash()
            post_cmd_head = self.get_current_head()
            contract_ok = (rc == 0)

            # Invariant: Non-mutation nodes must never alter HEAD or working tree status
            if not is_mutation and self.is_git_repo:
                if post_cmd_head != pre_node_head:
                    print(f"[ERROR] Non-mutation node '{node_id}' moved HEAD autonomously!", file=sys.stderr)
                    contract_ok = False
                    rc = 1
                if diff_hash != pre_node_hash:
                    print(f"[ERROR] Non-mutation node '{node_id}' modified tracked or untracked files!", file=sys.stderr)
                    contract_ok = False
                    rc = 1

            # Invariant: Mutation nodes must NEVER commit by themselves (runner owns commits)
            if is_mutation and self.is_git_repo and post_cmd_head != pre_node_head:
                print(f"[ERROR] Mutation node '{node_id}' moved HEAD autonomously (self-committing is prohibited)!", file=sys.stderr)
                contract_ok = False
                rc = 1

            # Enforce mutation boundaries over status AND diff paths
            if rc == 0 and is_mutation and contract_ok:
                try:
                    self.enforce_mutation_boundaries(node, pre_node_head)
                except Exception as e:
                    print(f"[ERROR] Mutation boundary violated: {e}", file=sys.stderr)
                    contract_ok = False
                    rc = 1

            commit_sha = None
            if rc == 0 and is_mutation and contract_ok and self.is_git_repo:
                run_cmd(["git", "add", "."], cwd=self.workdir)
                commit_msg = (
                    f"graph({self.graph_id}): node {node_id} success\n\n"
                    "Evolution-Check: none\n"
                    "Justification: automated graph node mutation commit"
                )
                commit_cmd = ["git", "commit", "-m", commit_msg]
                rc_commit, commit_out, commit_err = run_cmd(commit_cmd, cwd=self.workdir)
                if rc_commit != 0:
                    print(f"[ERROR] git commit failed for node '{node_id}': {commit_err or commit_out}", file=sys.stderr)
                    contract_ok = False
                    rc = 1
                else:
                    commit_sha = self.get_current_head()

            self.record_receipt(
                node_id, attempt=attempts, exit_code=rc, contract_ok=contract_ok,
                diff_hash=diff_hash, commit_sha=commit_sha,
                stdout_hash=stdout_hash, stderr_hash=stderr_hash
            )

            if rc == 0 and contract_ok:
                print(f"[NODE {node_id}] SUCCESS")
                self.completed_nodes.add(node_id)
                return True

            print(f"[NODE {node_id}] Attempt {attempts} failed with exit code {rc}")
            if attempts > self.max_retries:
                break

        # Node exhausted retries
        self.failed_nodes.add(node_id)
        escalation = node.get("failure_escalation", "rollback_and_halt")
        print(f"[NODE {node_id}] Failure escalation: {escalation}", file=sys.stderr)

        if escalation == "fallback_node":
            fb_id = node.get("fallback_node_id")
            if fb_id and fb_id in self.nodes:
                print(f"[FALLBACK] Resetting debris and substituting node '{node_id}' with fallback node '{fb_id}'")
                if is_mutation and self.is_git_repo and pre_node_head:
                    run_cmd(["git", "reset", "--hard", pre_node_head], cwd=self.workdir)
                    run_cmd(["git", "clean", "-fd"], cwd=self.workdir)

                fb_success = self.execute_node(fb_id)
                if fb_success:
                    self.completed_nodes.add(node_id)  # Mark original as substituted
                    return True
            print(f"Fallback node '{fb_id}' failed or missing", file=sys.stderr)
            return False
        else:
            print(f"Node '{node_id}' exhausted all {self.max_retries} retries", file=sys.stderr)
            return False

    def run(self) -> int:
        """Execute the DAG with deterministic manifest-order scheduling and main-thread rollback."""
        print(f"=== Starting Graph Run: {self.graph_id} ({self.run_id}) ===")
        print(f"Workdir: {self.workdir} | Approval: {self.approval_mode} | Receipts: {self.receipts_file}")

        try:
            self.validate_manifest_integrity()
            self.verify_clean_git()
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        self.save_state("running")
        success = False

        try:
            # Separate primary nodes and fallback nodes
            primary_nodes = {nid: n for nid, n in self.nodes.items() if nid not in self.fallback_nodes}

            # Validate workspace requirement
            mutations = [n for n in primary_nodes.values() if n.get("type") == "sequential_mutation"]
            if mutations and not self.is_git_repo:
                print("ERROR: Mutations require a git workspace. Use --worktree or --create-worktree.", file=sys.stderr)
                self.rollback_and_halt("Mutations require a git workspace")
                return 1

            # Manifest-order execution loop
            remaining = set(primary_nodes.keys())
            while remaining:
                ready_nodes = [
                    n["id"] for n in self.nodes_list
                    if n["id"] in remaining and all(dep in self.completed_nodes for dep in n.get("depends_on", []))
                ]

                if not ready_nodes:
                    self.rollback_and_halt("Deadlock detected: No eligible nodes ready to run")
                    return 1

                parallel_reads = [nid for nid in ready_nodes if primary_nodes[nid].get("type") == "parallel_read"]
                other_ready = [nid for nid in ready_nodes if primary_nodes[nid].get("type") != "parallel_read"]

                if parallel_reads:
                    pre_hash = self.get_porcelain_hash()
                    pre_head = self.get_current_head()
                    batch = parallel_reads[:self.max_concurrency]
                    print(f"[PARALLEL BATCH] Running {len(batch)} parallel read node(s)...")

                    batch_failed = False
                    with ThreadPoolExecutor(max_workers=self.max_concurrency) as pool:
                        futures = {pool.submit(self.execute_node, nid): nid for nid in batch}
                        for f in as_completed(futures):
                            nid = futures[f]
                            try:
                                res = f.result()
                                if not res:
                                    batch_failed = True
                                else:
                                    remaining.remove(nid)
                            except Exception as e:
                                print(f"[ERROR] Worker exception on node '{nid}': {e}", file=sys.stderr)
                                batch_failed = True

                    if batch_failed:
                        self.rollback_and_halt("Parallel read node failed execution")
                        return 1

                    # Barrier check post parallel batch
                    post_hash = self.get_porcelain_hash()
                    post_head = self.get_current_head()
                    if pre_hash != post_hash or pre_head != post_head:
                        self.rollback_and_halt("Barrier integrity check failed: Parallel read phase modified tracked files or moved HEAD.")
                        return 1

                elif other_ready:
                    nid = other_ready[0]
                    node_ok = self.execute_node(nid)
                    if not node_ok:
                        self.rollback_and_halt(f"Node '{nid}' execution failed")
                        return 1
                    remaining.remove(nid)

            success = True
            self.save_state("success")
            print(f"=== Graph Run SUCCESS: All {len(primary_nodes)} primary nodes completed. ===")
            print(f"Receipts saved to: {self.receipts_file}")
            return 0
        except BaseException as e:
            if not success:
                self.rollback_and_halt(f"Run aborted due to exception: {e}")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Graph Manifest Runner")
    parser.add_argument("manifest", help="Path to graph-manifest.json file")
    parser.add_argument("--worktree", help="Path to existing git worktree directory")
    parser.add_argument("--create-worktree", action="store_true", help="Create new git worktree and run in it")
    parser.add_argument("--base", default="HEAD", help="Base git ref for --create-worktree (default: HEAD)")
    parser.add_argument("--no-workspace", action="store_true", help="Run in current directory (read-only DAGs only)")
    parser.add_argument("--approval", choices=["prompt", "none"], default="prompt",
                        help="Approval mode: 'prompt' (interactive) or 'none' (requires --expect-manifest-sha256 for mutations)")
    parser.add_argument("--expect-manifest-sha256", help="Expected SHA256 hex digest of approved manifest")
    parser.add_argument("--run-dir", help="Directory where .graph-run receipt and state records are stored")

    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"ERROR: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to read or parse manifest {manifest_path}: {e}", file=sys.stderr)
        sys.exit(1)

    mutations = [n for n in manifest.get("nodes", []) if n.get("type") == "sequential_mutation"]

    if args.no_workspace:
        if mutations:
            print("ERROR: --no-workspace is prohibited for graphs containing sequential_mutation nodes. "
                  "Mutations require an isolated git worktree.", file=sys.stderr)
            sys.exit(1)
        workdir = Path.cwd()
        run_id = None
    elif args.create_worktree:
        run_id = f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        worktree_path = Path(".worktrees") / f"graph-{run_id}"
        worktree_path.parent.mkdir(parents=True, exist_ok=True)
        rc, _, err = run_cmd(["git", "worktree", "add", "-b", f"graph-{run_id}", str(worktree_path), args.base])
        if rc != 0:
            print(f"ERROR: Failed to create git worktree at {worktree_path}: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Created isolated worktree at: {worktree_path}")
        workdir = worktree_path
    elif args.worktree:
        workdir = Path(args.worktree)
        if not workdir.is_dir():
            print(f"ERROR: Specified worktree directory does not exist: {workdir}", file=sys.stderr)
            sys.exit(1)
        run_id = None
    else:
        if mutations:
            print("ERROR: Manifest contains mutations. You must specify --worktree <path> or --create-worktree.", file=sys.stderr)
            sys.exit(1)
        workdir = Path.cwd()
        run_id = None

    custom_run_dir = Path(args.run_dir) if args.run_dir else None

    runner = GraphRunner(
        manifest_path=manifest_path,
        workdir=workdir,
        approval_mode=args.approval,
        run_id=run_id,
        run_dir=custom_run_dir,
        expected_manifest_sha=args.expect_manifest_sha256,
        parsed_manifest=(manifest, manifest_bytes)
    )
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
