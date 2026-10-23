#!/usr/bin/env python3
"""
Regression tests for graph-planner / graph-execution bug fixes.

Purpose:
    Lock in fixes to graph_runner.py and validate_manifest.py found during the 2026-10-18 review.

Key Input Dependencies:
    plugins/agent-orchestration/scripts/graph_runner.py, validate_manifest.py, and
    references/graph-manifest-schema.json; a local git binary for temporary test repositories.

Validates:
- verifier_hash binds the script named after an interpreter (tampered script is rejected)
- A mutation node that produces no changes succeeds without a commit
- Fallback mutations validate and substitute at their primary's chain position
- Fallback ordering and type-mismatch violations are rejected
- --no-workspace failures never reset or clean the caller's checkout
- Irreversible nodes require the approval gate and manifest SHA under --approval none
- graph_id cannot steer the run directory outside run_dir before validation
- Validator reports (does not crash on) malformed nodes
"""

import sys
import json
import subprocess
import shutil
import tempfile
import unittest
from pathlib import Path

PLUGIN_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(PLUGIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PLUGIN_SCRIPTS))

from graph_runner import GraphRunner, compute_file_sha256
from validate_manifest import validate_graph_topology


def run_cmd(cmd, cwd):
    """Run a subprocess and return (returncode, stdout, stderr)."""
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr


def node(nid, ntype="parallel_read", cmd="true", deps=None, **extra):
    """Build a schema-valid manifest node with sensible defaults."""
    tier = "deterministic_script" if ntype == "verifier_gate" else "fast_engine"
    n = {
        "id": nid,
        "type": ntype,
        "tier": tier,
        "command_or_eval": cmd,
        "input_bindings": [],
        "output_contract": "out.json",
        "depends_on": deps or [],
        "failure_escalation": "rollback_and_halt",
    }
    n.update(extra)
    return n


def manifest(graph_id, nodes, retries=0):
    """Build a schema-valid manifest wrapping the given nodes."""
    return {
        "schema_version": "1.0.0",
        "graph_id": graph_id,
        "version": "1.0.0",
        "budget": {"token_ceiling_total": 5000, "max_parallel_concurrency": 2, "max_retries_per_node": retries},
        "nodes": nodes,
    }


GATE = node("gate", "verifier_gate", role="approval")


class GraphFixTestBase(unittest.TestCase):

    def setUp(self):
        """Create a temporary git repository with a committed verifier script."""
        self.temp_dir = tempfile.mkdtemp(prefix="test_graph_fixes_")
        self.workdir = Path(self.temp_dir)
        run_cmd(["git", "init"], cwd=self.workdir)
        run_cmd(["git", "config", "user.name", "Test Runner"], cwd=self.workdir)
        run_cmd(["git", "config", "user.email", "test@runner.local"], cwd=self.workdir)
        run_cmd(["git", "config", "commit.gpgsign", "false"], cwd=self.workdir)
        (self.workdir / "README.md").write_text("# Initial Repo\n")
        (self.workdir / "verify.sh").write_text("exit 0\n")
        run_cmd(["git", "add", "."], cwd=self.workdir)
        run_cmd(["git", "commit", "-m", "initial commit"], cwd=self.workdir)
        self.manifest_dir = Path(tempfile.mkdtemp(prefix="test_graph_fixes_manifest_"))

    def tearDown(self):
        """Remove the temporary repository and manifest directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.manifest_dir, ignore_errors=True)

    def _write(self, data) -> Path:
        """Write manifest data to a file outside the repository and return its path."""
        path = self.manifest_dir / "graph-manifest.json"
        path.write_text(json.dumps(data, indent=2))
        return path

    def _run(self, data, approval="none"):
        """Run the manifest under the given approval mode with its SHA bound; return (runner, exit code)."""
        path = self._write(data)
        runner = GraphRunner(manifest_path=path, workdir=self.workdir, approval_mode=approval,
                             expected_manifest_sha=compute_file_sha256(path))
        return runner, runner.run()

    def _head(self):
        """Return the repository's current HEAD SHA."""
        return run_cmd(["git", "rev-parse", "HEAD"], cwd=self.workdir)[1].strip()


class TestVerifierHash(GraphFixTestBase):

    def test_script_behind_interpreter_is_bound(self):
        """Script behind interpreter is bound."""
        good_hash = compute_file_sha256(self.workdir / "verify.sh")
        data = manifest("verifier-bind", [node("check", "verifier_gate", cmd="bash verify.sh", verifier_hash=good_hash)])
        _, rc = self._run(data)
        self.assertEqual(rc, 0, "Untampered script behind an interpreter must pass")

        (self.workdir / "verify.sh").write_text("exit 0 # tampered\n")
        run_cmd(["git", "commit", "-qam", "tamper"], cwd=self.workdir)
        _, rc = self._run(data)
        self.assertEqual(rc, 1, "Tampered script behind an interpreter must fail the verifier hash")

    def test_command_without_file_hashes_command_string(self):
        """Command without file hashes command string."""
        import hashlib
        cmd = "test -f README.md"
        cmd_hash = hashlib.sha256(cmd.encode("utf-8")).hexdigest()
        # README.md is a file token, so the file is hashed, not the string
        data = manifest("verifier-file-token", [node("check", "verifier_gate", cmd=cmd, verifier_hash=cmd_hash)])
        _, rc = self._run(data)
        self.assertEqual(rc, 1)
        cmd2 = "true"
        data2 = manifest("verifier-string", [node("check", "verifier_gate", cmd=cmd2,
                                                  verifier_hash=hashlib.sha256(cmd2.encode()).hexdigest())])
        _, rc2 = self._run(data2)
        self.assertEqual(rc2, 0)


class TestNoOpMutation(GraphFixTestBase):

    def test_mutation_without_changes_succeeds_without_commit(self):
        """Mutation without changes succeeds without commit."""
        start = self._head()
        data = manifest("noop-mutation", [
            GATE,
            node("mut", "sequential_mutation", cmd="true", deps=["gate"], mutation_targets=["README.md"]),
        ])
        runner, rc = self._run(data)
        self.assertEqual(rc, 0, "Idempotent mutation that changes nothing must succeed")
        self.assertEqual(self._head(), start, "No commit must be created for a no-op mutation")
        receipts = [json.loads(l) for l in runner.receipts_file.read_text().splitlines() if l.strip()]
        self.assertIsNone([r for r in receipts if r["node_id"] == "mut"][0]["commit_sha"])


class TestMutationFallback(GraphFixTestBase):

    def _fallback_graph(self, fb_deps):
        """Build a four-mutation chain whose m2 falls back to m2fb with the given dependencies."""
        return manifest("mutation-fallback", [
            GATE,
            node("m1", "sequential_mutation", cmd="echo a > a.txt", deps=["gate"], mutation_targets=["a.txt"]),
            node("m2", "sequential_mutation", cmd="false", deps=["m1"], mutation_targets=["b.txt"],
                 failure_escalation="fallback_node", fallback_node_id="m2fb"),
            node("m2fb", "sequential_mutation", cmd="echo b > b.txt", deps=fb_deps, role="fallback",
                 mutation_targets=["b.txt"]),
            node("m3", "sequential_mutation", cmd="echo c > c.txt", deps=["m2"], mutation_targets=["c.txt"]),
        ])

    def test_fallback_mutation_validates_and_substitutes(self):
        """Fallback mutation validates and substitutes."""
        data = self._fallback_graph(["m1"])
        self.assertEqual(validate_graph_topology(data, check_approval_none=True), [])
        runner, rc = self._run(data)
        self.assertEqual(rc, 0, "Fallback mutation must substitute for its failed primary")
        for name in ("a.txt", "b.txt", "c.txt"):
            self.assertTrue((self.workdir / name).exists(), f"{name} must exist after substitution")
        self.assertEqual(runner.substituted_nodes, {"m2": "m2fb"})
        self.assertNotIn("m2", runner.failed_nodes)

    def test_fallback_out_of_position_rejected(self):
        """Fallback out of position rejected."""
        data = self._fallback_graph(["gate"])  # skips m1, unlike its primary
        errs = validate_graph_topology(data)
        self.assertTrue(any("Fallback ordering violation" in e for e in errs), errs)

    def test_fallback_type_mismatch_rejected(self):
        """Fallback type mismatch rejected."""
        data = manifest("fb-type", [
            node("read", failure_escalation="fallback_node", fallback_node_id="fb"),
            node("fb", "sequential_mutation", role="fallback", mutation_targets=["x.txt"]),
        ])
        errs = validate_graph_topology(data)
        self.assertTrue(any("Fallback type mismatch" in e for e in errs), errs)


class TestNoWorkspaceNonDestructive(GraphFixTestBase):

    def test_failed_read_does_not_reset_callers_checkout(self):
        """Failed read does not reset callers checkout."""
        (self.workdir / "user_wip.txt").write_text("unsaved user work\n")
        with open(self.workdir / "README.md", "a") as f:
            f.write("user edit\n")
        path = self._write(manifest("nows-fail", [node("scan", cmd="grep -q nothing-matches README.md")]))
        rc, out, err = run_cmd([sys.executable, str(PLUGIN_SCRIPTS / "graph_runner.py"), str(path),
                                "--no-workspace", "--approval", "none"], cwd=self.workdir)
        self.assertEqual(rc, 1)
        self.assertIn("Non-destructive mode", err)
        self.assertTrue((self.workdir / "user_wip.txt").exists(), "Untracked user work must survive")
        self.assertIn("user edit", (self.workdir / "README.md").read_text(), "Tracked user edit must survive")

    def test_dirty_checkout_allowed_for_readonly_no_workspace(self):
        """Dirty checkout allowed for readonly no workspace."""
        (self.workdir / "user_wip.txt").write_text("unsaved user work\n")
        path = self._write(manifest("nows-ok", [node("scan", cmd="cat README.md")]))
        rc, _, err = run_cmd([sys.executable, str(PLUGIN_SCRIPTS / "graph_runner.py"), str(path),
                              "--no-workspace", "--approval", "none"], cwd=self.workdir)
        self.assertEqual(rc, 0, err)


class TestIrreversibleGating(GraphFixTestBase):

    def test_irreversible_read_requires_approval_gate(self):
        """Irreversible read requires approval gate."""
        data = manifest("irrev", [node("post", cmd="true", reversible=False)])
        errs = validate_graph_topology(data, check_approval_none=True)
        self.assertTrue(any("Approval gate violation" in e for e in errs), errs)

        gated = manifest("irrev", [GATE, node("post", cmd="true", deps=["gate"], reversible=False)])
        self.assertEqual(validate_graph_topology(gated, check_approval_none=True), [])

    def test_irreversible_requires_manifest_sha_under_none(self):
        """Irreversible requires manifest sha under none."""
        path = self._write(manifest("irrev-sha", [GATE, node("post", cmd="true", deps=["gate"], reversible=False)]))
        runner = GraphRunner(manifest_path=path, workdir=self.workdir, approval_mode="none")
        self.assertEqual(runner.run(), 1)


class TestManifestHardening(GraphFixTestBase):

    def test_graph_id_cannot_escape_run_dir(self):
        """Graph id cannot escape run dir."""
        run_dir = Path(tempfile.mkdtemp(prefix="test_graph_fixes_rundir_"))
        try:
            data = manifest("ok", [node("scan")])
            data["graph_id"] = "../../escaped"
            path = self._write(data)
            runner = GraphRunner(manifest_path=path, workdir=self.workdir, approval_mode="none", run_dir=run_dir)
            self.assertTrue(str(runner.run_dir.resolve()).startswith(str(run_dir.resolve())))
            self.assertEqual(runner.run(), 1, "Invalid graph_id must still fail validation")
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)

    def test_validator_reports_malformed_nodes(self):
        """Validator reports malformed nodes."""
        data = manifest("malformed", [
            "not-a-node",
            {"type": "sequential_mutation"},
            node("a", "sequential_mutation", deps=["gate", {"bad": 1}], mutation_targets=["x"]),
            GATE,
        ])
        errs = validate_graph_topology(data, check_approval_none=True)
        self.assertTrue(any("is not an object" in e for e in errs), errs)
        self.assertTrue(any("missing 'id'" in e for e in errs), errs)
        self.assertTrue(any("array of node ID strings" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
