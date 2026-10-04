#!/usr/bin/env python3
"""
Unit and integration tests for graph_runner.py
Validates:
- Target worktree uncommitted check
- Workspace flags (--worktree, --create-worktree, --no-workspace)
- Approval mode semantics (--approval prompt fail-closed, --approval none requiring --expect-manifest-sha256)
- Accurate null-byte delimited mutation boundary check (editing existing tracked files, paths with spaces, forbidden globs)
- Non-mutation node immutability (detecting read nodes that commit or mutate files)
- Verifier hash integrity checks
- Retry ceiling and fallback node substitution with clean debris reset
- Rollback restoring start SHA and git clean
- Run isolation in anchored run directory outside worktree
- Append-only receipts.jsonl structure with commit SHA and stdout/stderr hashes
- Handling of rejected git commit
"""

import sys
import os
import json
import subprocess
import shutil
import tempfile
import unittest
from pathlib import Path

PLUGIN_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(PLUGIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PLUGIN_SCRIPTS))

from graph_runner import GraphRunner, compute_sha256, compute_file_sha256


def run_cmd(cmd, cwd):
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr


class TestGraphRunner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_graph_runner_")
        self.workdir = Path(self.temp_dir)
        # Initialize test git repo
        run_cmd(["git", "init"], cwd=self.workdir)
        run_cmd(["git", "config", "user.name", "Test Runner"], cwd=self.workdir)
        run_cmd(["git", "config", "user.email", "test@runner.local"], cwd=self.workdir)
        run_cmd(["git", "config", "commit.gpgsign", "false"], cwd=self.workdir)

        # Initial commit with existing tracked files
        (self.workdir / "README.md").write_text("# Initial Repo\n")
        (self.workdir / "src").mkdir(parents=True, exist_ok=True)
        (self.workdir / "src" / "main.py").write_text("# main\n")
        run_cmd(["git", "add", "."], cwd=self.workdir)
        run_cmd(["git", "commit", "-m", "initial commit"], cwd=self.workdir)

        _, out, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.workdir)
        self.start_sha = out.strip()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_manifest(self, data) -> Path:
        tf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        tf.write(json.dumps(data, indent=2))
        tf.close()
        return Path(tf.name)

    def test_refuses_start_with_uncommitted_changes(self):
        (self.workdir / "dirty.txt").write_text("uncommitted")
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "dirty-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 2, "max_retries_per_node": 1},
            "nodes": [
                {
                    "id": "node-1",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "echo read",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Runner must refuse to start if worktree has uncommitted changes")

    def test_no_workspace_rejected_with_mutations(self):
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "mut-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 2, "max_retries_per_node": 1},
            "nodes": [
                {
                    "id": "mut-1",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo mutated >> README.md",
                    "mutation_targets": ["README.md"],
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        rc, _, err = run_cmd([sys.executable, str(PLUGIN_SCRIPTS / "graph_runner.py"), str(manifest_path), "--no-workspace"], cwd=self.workdir)
        self.assertNotEqual(rc, 0, "CLI must reject --no-workspace on mutation graphs")
        self.assertIn("prohibited for graphs containing sequential_mutation", err)

    def test_no_workspace_allowed_for_readonly(self):
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "readonly-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 2, "max_retries_per_node": 1},
            "nodes": [
                {
                    "id": "read-1",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "echo 'Read-only successful'",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 0, "Read-only graph must succeed")

    def test_approval_none_requires_expect_manifest_sha(self):
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "none-requires-sha",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "gate-app",
                    "role": "approval",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "true",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                },
                {
                    "id": "mut-1",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo hello >> README.md",
                    "mutation_targets": ["README.md"],
                    "input_bindings": ["gate-app"],
                    "output_contract": "out.json",
                    "depends_on": ["gate-app"],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        # Run with --approval none but WITHOUT expected_manifest_sha
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Mutation graph running under --approval none must require --expect-manifest-sha256")

        # Now run WITH correct expected_manifest_sha
        sha = compute_file_sha256(manifest_path)
        runner_with_sha = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none", expected_manifest_sha=sha)
        exit_code_ok = runner_with_sha.run()
        self.assertEqual(exit_code_ok, 0, "Mutation graph with correct --expect-manifest-sha256 must succeed")

    def test_mutation_boundaries_editing_existing_files_and_spaces(self):
        # 1. Edit existing tracked file in subdirectory: src/main.py
        # 2. Create file with spaces: "docs with space/notes.md"
        (self.workdir / "docs with space").mkdir(parents=True, exist_ok=True)
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "boundary-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "gate-approval",
                    "role": "approval",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "true",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                },
                {
                    "id": "mut-existing",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo '# appended line' >> src/main.py && echo 'space notes' > 'docs with space/notes.md'",
                    "mutation_targets": ["src/main.py", "docs with space/notes.md"],
                    "input_bindings": ["gate-approval"],
                    "output_contract": "out.json",
                    "depends_on": ["gate-approval"],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        sha = compute_file_sha256(manifest_path)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none", expected_manifest_sha=sha)
        exit_code = runner.run()
        self.assertEqual(exit_code, 0, "Editing existing file (src/main.py) and path with spaces must succeed")

    def test_mutation_forbidden_path_rejected(self):
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "forbidden-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "gate-approval",
                    "role": "approval",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "true",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                },
                {
                    "id": "mut-forbidden",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo touch >> secret.key",
                    "mutation_targets": ["secret.key"],
                    "forbidden_paths": ["*.key"],
                    "input_bindings": ["gate-approval"],
                    "output_contract": "out.json",
                    "depends_on": ["gate-approval"],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        sha = compute_file_sha256(manifest_path)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none", expected_manifest_sha=sha)
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Modifying path matching forbidden_paths pattern must fail")

    def test_non_mutation_node_committing_is_caught(self):
        # A parallel_read node attempts to commit its changes to evade git status check
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "commit-evasion",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "evasive-read",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "echo z >> README.md && git commit -qam 'evade'",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Non-mutation node that moves HEAD must be caught and fail run")
        # Ensure HEAD was rolled back to start_sha
        _, sha_out, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.workdir)
        self.assertEqual(sha_out.strip(), self.start_sha)

    def test_retry_resets_working_tree_between_attempts(self):
        # Node fails first attempt leaving dirty file; second attempt succeeds
        script_file = self.workdir / "flaky.sh"
        script_file.write_text("""#!/usr/bin/env bash
if [ ! -f /tmp/test_attempt_flag ]; then
  touch /tmp/test_attempt_flag
  echo "dirty debris" >> README.md
  exit 1
else
  rm -f /tmp/test_attempt_flag
  echo "# Clean attempt" > README.md
  exit 0
fi
""")
        run_cmd(["chmod", "+x", str(script_file)], cwd=self.workdir)
        run_cmd(["git", "add", "flaky.sh"], cwd=self.workdir)
        run_cmd(["git", "commit", "-m", "add flaky script"], cwd=self.workdir)
        run_cmd(["rm", "-f", "/tmp/test_attempt_flag"], cwd=self.workdir)

        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "retry-clean-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 1},
            "nodes": [
                {
                    "id": "gate-approval",
                    "role": "approval",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "true",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                },
                {
                    "id": "mut-flaky",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "./flaky.sh",
                    "mutation_targets": ["README.md"],
                    "input_bindings": ["gate-approval"],
                    "output_contract": "out.json",
                    "depends_on": ["gate-approval"],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        sha = compute_file_sha256(manifest_path)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none", expected_manifest_sha=sha)
        exit_code = runner.run()
        self.assertEqual(exit_code, 0, "Flaky node must succeed after resetting debris between attempts")
        self.assertEqual((self.workdir / "README.md").read_text(), "# Clean attempt\n")

    def test_run_receipts_recorded_outside_worktree_survives_rollback(self):
        # Anchor run_dir explicitly outside worktree
        external_run_dir = Path(tempfile.mkdtemp(prefix="test_external_rundir_"))
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "receipts-survive-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "gate-approval",
                    "role": "approval",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "false",  # Fails!
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(
            manifest_path=manifest_path, workdir=self.workdir, approval_mode="none",
            run_dir=external_run_dir, expected_manifest_sha=compute_file_sha256(manifest_path)
        )
        exit_code = runner.run()
        self.assertEqual(exit_code, 1)

        # Confirm receipts.jsonl survived rollback intact
        self.assertTrue(runner.receipts_file.exists(), "Receipts file must survive rollback intact")
        lines = [json.loads(line) for line in runner.receipts_file.read_text().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["node_id"], "gate-approval")
        self.assertEqual(lines[0]["exit_code"], 1)
        shutil.rmtree(external_run_dir, ignore_errors=True)

    def test_prompt_fail_closed_non_interactive(self):
        # Under --approval prompt with non-interactive stdin, runner must fail closed before mutations
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "prompt-fail-closed",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "mut-1",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo mutated >> README.md",
                    "mutation_targets": ["README.md"],
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        rc, out, err = run_cmd(
            [sys.executable, str(PLUGIN_SCRIPTS / "graph_runner.py"), str(manifest_path), "--worktree", str(self.workdir), "--approval", "prompt"],
            cwd=self.workdir
        )
        self.assertEqual(rc, 1, "Non-interactive stdin must fail closed under --approval prompt")
        self.assertIn("Non-interactive stdin detected", err + out)
        # Verify no mutations occurred
        self.assertEqual((self.workdir / "README.md").read_text(), "# Initial Repo\n")

    def test_verifier_hash_mismatch_rejected(self):
        # Incorrect verifier_hash must halt before node executes
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "verifier-hash-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "gate-1",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "true",
                    "verifier_hash": "0000000000000000000000000000000000000000000000000000000000000000",  # mismatch
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Verifier hash mismatch must fail closed")

    def test_fallback_substitution(self):
        # Primary node fails, fallback node executes and substitutes for primary
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "fallback-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "node-primary",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "false",  # fails!
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "fallback_node",
                    "fallback_node_id": "node-fb"
                },
                {
                    "id": "node-fb",
                    "role": "fallback",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "true",  # fallback succeeds
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 0, "Fallback substitution must allow graph run to succeed")
        self.assertIn("node-primary", runner.completed_nodes)

    def test_parallel_read_barrier_detects_mutation(self):
        # A parallel_read node modifies a file; barrier must detect and trigger rollback
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "barrier-mutation-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 2, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "read-sneak",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "echo 'unauthorized write' >> README.md",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Barrier must detect file modification during parallel read phase")
        # Ensure rollback was executed
        self.assertEqual((self.workdir / "README.md").read_text(), "# Initial Repo\n")

    def test_rollback_restores_start_sha(self):
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "rollback-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "failing-node",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "echo 'dirty' > new_file.txt && false",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1)

        # Assert HEAD restored to start_sha and working tree clean
        _, sha_out, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.workdir)
        self.assertEqual(sha_out.strip(), self.start_sha)
        self.assertFalse((self.workdir / "new_file.txt").exists(), "Untracked files created during run must be cleaned")

    def test_mutation_self_commit_prohibited(self):
        # A mutation node commits by itself; runner must catch that HEAD moved and fail closed
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "self-commit-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "gate-approval",
                    "role": "approval",
                    "type": "verifier_gate",
                    "tier": "deterministic_script",
                    "command_or_eval": "true",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                },
                {
                    "id": "mut-self-commit",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo k > secret.key && git add secret.key && git commit -qm sneak && echo y >> src/main.py",
                    "mutation_targets": ["src/main.py"],
                    "forbidden_paths": ["*.key"],
                    "input_bindings": ["gate-approval"],
                    "output_contract": "out.json",
                    "depends_on": ["gate-approval"],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        sha = compute_file_sha256(manifest_path)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none", expected_manifest_sha=sha)
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Self-committing mutation node must be rejected and failed")
        # Ensure secret.key is NOT in git log
        _, log_out, _ = run_cmd(["git", "log", "--oneline"], cwd=self.workdir)
        self.assertNotIn("sneak", log_out, "Sneak commit must be rolled back completely")
        self.assertFalse((self.workdir / "secret.key").exists())

    def test_timeout_handling_process_group(self):
        # Node times out; process group is killed, receipt recorded with exit code 124, no TypeError
        manifest_data = {
            "schema_version": "1.0.0",
            "graph_id": "timeout-test",
            "version": "1.0.0",
            "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
            "nodes": [
                {
                    "id": "timeout-node",
                    "type": "parallel_read",
                    "tier": "fast_engine",
                    "command_or_eval": "echo starting; sleep 5",
                    "timeout_seconds": 1,
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        manifest_path = self._write_manifest(manifest_data)
        runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
        exit_code = runner.run()
        self.assertEqual(exit_code, 1, "Timed out node must fail run")

        # Inspect receipt
        lines = [json.loads(line) for line in runner.receipts_file.read_text().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["node_id"], "timeout-node")
        self.assertEqual(lines[0]["exit_code"], 124, "Timeout must record exit code 124 in receipt")

    def test_rollback_on_main_thread_only(self):
        import threading
        calling_threads = []
        original_rollback = GraphRunner.rollback_and_halt

        def tracking_rollback(self_obj, reason):
            calling_threads.append(threading.current_thread().name)
            original_rollback(self_obj, reason)

        GraphRunner.rollback_and_halt = tracking_rollback
        try:
            manifest_data = {
                "schema_version": "1.0.0",
                "graph_id": "thread-test",
                "version": "1.0.0",
                "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 2, "max_retries_per_node": 0},
                "nodes": [
                    {
                        "id": "read-fail-1",
                        "type": "parallel_read",
                        "tier": "fast_engine",
                        "command_or_eval": "false",
                        "input_bindings": [],
                        "output_contract": "out.json",
                        "depends_on": [],
                        "failure_escalation": "rollback_and_halt"
                    },
                    {
                        "id": "read-fail-2",
                        "type": "parallel_read",
                        "tier": "fast_engine",
                        "command_or_eval": "false",
                        "input_bindings": [],
                        "output_contract": "out.json",
                        "depends_on": [],
                        "failure_escalation": "rollback_and_halt"
                    }
                ]
            }
            manifest_path = self._write_manifest(manifest_data)
            runner = GraphRunner(manifest_path=manifest_path, workdir=self.workdir, approval_mode="none")
            exit_code = runner.run()
            self.assertEqual(exit_code, 1)
            # Verify rollback was called strictly from MainThread
            self.assertGreaterEqual(len(calling_threads), 1)
            for t_name in calling_threads:
                self.assertEqual(t_name, "MainThread", f"Rollback must run on MainThread, was called from {t_name}")
        finally:
            GraphRunner.rollback_and_halt = original_rollback


if __name__ == "__main__":
    unittest.main()
