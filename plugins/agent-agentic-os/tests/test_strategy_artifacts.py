"""
test_strategy_artifacts.py — Test Data-Driven Strategy Artifacts and Manifest Binding (PR B)
=============================================================================================

Validates:
1. TransitionRegistry loads strategy_artifacts from transition_templates.yaml.
2. TransitionCoordinator detects declared strategy and validates strategy-specific plan artifacts.
3. If declared strategy is 'graph', graph-manifest.json is required and validated via validate_manifest.py.
4. If manifest validation fails, transition to PLAN_REVIEW is rejected with clear diagnostics.
5. If validator script is missing, coordinator fails closed.
6. Gate 1 content snapshot binds graph-manifest.json when present for the task.
"""

import hashlib
import io
import json
import os
import shlex
import shutil
import sqlite3
import tempfile
from pathlib import Path
import pytest

from control_plane.registry import TransitionRegistry, TransitionTemplate
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.snapshot import gate1_artifact_paths, build_snapshot
from control_plane.ports import FilesystemPort


class MockFilesystemPort(FilesystemPort):
    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    def read_text(self, path: Path, encoding: str = "utf-8") -> str:
        return path.read_text(encoding=encoding)

    def write_text(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)

    def append_text(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding=encoding) as f:
            f.write(content)


class MockClock:
    def current_time(self) -> float:
        return 1700000000.0


class MockCrypto:
    def sha256_hex(self, data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class MockControlPlane:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self._clock = MockClock()
        self._crypto = MockCrypto()
        self._receipts = []
        self._conn = sqlite3.connect(":memory:")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transition_request (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                to_state TEXT,
                status TEXT,
                content_snapshot TEXT
            )
            """
        )

    def get_verification_receipts(self, task_id: str):
        return list(self._receipts)

    def record_receipt(self, receipt):
        self._receipts.append(receipt)


def test_registry_loads_strategy_artifacts():
    registry = TransitionRegistry.load_default()
    artifacts = registry.strategy_artifacts
    assert "graph" in artifacts
    assert "dual-loop" in artifacts
    assert "agent-swarm" in artifacts
    assert "direct" in artifacts

    graph_cfg = registry.get_strategy_artifact_config("graph")
    assert graph_cfg is not None
    assert "graph-manifest.json" in graph_cfg["artifact"]
    assert "validate_manifest.py" in (graph_cfg.get("validator_script") or graph_cfg["validator"][1])


def test_gate1_snapshot_binds_manifest_when_present(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-test-42"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan", encoding="utf-8")

    # Without manifest
    paths_without = gate1_artifact_paths(repo, task_id)
    assert len(paths_without) == 2
    assert [p[0] for p in paths_without] == ["spec", "plan"]

    # With manifest
    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text('{"graph_id": "test"}', encoding="utf-8")

    paths_with = gate1_artifact_paths(repo, task_id)
    assert len(paths_with) == 3
    assert [p[0] for p in paths_with] == ["spec", "plan", "manifest"]

    snapshot = build_snapshot(paths_with)
    assert len(snapshot) == 3
    assert snapshot[2].label == "manifest"
    assert snapshot[2].sha256 == hashlib.sha256(manifest_file.read_bytes()).hexdigest()


def _setup_test_repo(repo: Path):
    real_orch = Path(__file__).resolve().parents[3] / "plugins" / "agent-orchestration"
    plugins_dir = repo / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    orch_link = plugins_dir / "agent-orchestration"
    if not orch_link.exists():
        orch_link.symlink_to(real_orch)


def test_coordinator_graph_strategy_validates_and_stages_manifest(tmp_path):
    repo = tmp_path / "repo"
    _setup_test_repo(repo)
    task_id = "task-graph-1"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text(
        "# Plan\n\nExecution Strategy: graph\nRationale: Complex DAG with parallel fan-out\n",
        encoding="utf-8",
    )

    valid_manifest = {
        "schema_version": "1.0.0",
        "graph_id": "test-valid-graph",
        "version": "1.0.0",
        "budget": {
            "token_ceiling_total": 50000,
            "max_parallel_concurrency": 4,
            "max_retries_per_node": 2,
        },
        "nodes": [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "deterministic_script",
                "command_or_eval": "echo read",
                "timeout_seconds": 30,
                "depends_on": [],
                "input_bindings": [],
                "output_contract": {},
                "failure_escalation": "rollback_and_halt",
            }
        ],
    }
    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text(json.dumps(valid_manifest), encoding="utf-8")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    receipt = coord._stage_plan_artifact_submission(task_id, task, template)
    assert receipt is not None
    assert receipt["gate_name"] == "plan_artifact_submission"
    assert f"graph:{task_id}-graph-manifest.json=" in receipt["command_executed"]


def test_coordinator_graph_strategy_missing_manifest_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    _setup_test_repo(repo)
    task_id = "task-graph-missing"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text(
        "# Plan\n\nstrategy: graph\n",
        encoding="utf-8",
    )

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "Declared strategy 'graph' requires artifact" in str(exc_info.value)


def test_coordinator_graph_strategy_invalid_manifest_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    _setup_test_repo(repo)
    task_id = "task-graph-invalid"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text(
        "# Plan\n\nstrategy: graph\n",
        encoding="utf-8",
    )

    # Missing schema_version and missing timeout_seconds
    invalid_manifest = {
        "graph_id": "test-invalid-graph",
        "nodes": [
            {
                "id": "node-1",
                "type": "parallel_read",
                "command_or_eval": "echo read",
            }
        ],
    }
    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text(json.dumps(invalid_manifest), encoding="utf-8")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "artifact validation failed" in str(exc_info.value)


def test_coordinator_missing_validator_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-missing-val"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan\n\nstrategy: graph\n", encoding="utf-8")

    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text('{"schema_version": "1.0.0"}', encoding="utf-8")

    # repo does NOT have plugins/agent-orchestration installed!
    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "validator" in str(exc_info.value) and "is not installed" in str(exc_info.value)


def test_coordinator_unknown_strategy_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-unknown-strat"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan\n\nstrategy: grahp\n", encoding="utf-8")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "Declared execution strategy 'grahp' is unknown or not supported" in str(exc_info.value)


def test_coordinator_rollback_strategy_revert_not_treated_as_strategy(tmp_path):
    repo = tmp_path / "repo"
    _setup_test_repo(repo)
    task_id = "task-rollback-strat"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    # Contains 'Rollback strategy: revert the commit' which previously matched regex
    # and caused strategy to be 'revert', bypassing graph validation of garbage manifest!
    plan_file.write_text(
        "# Plan\n\n- Rollback strategy: revert the commit\n",
        encoding="utf-8",
    )

    # Garbage manifest present
    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text('{"bad": "manifest"}', encoding="utf-8")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    # Manifest exists, so declared_strategy detects "graph" and validates the manifest
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "artifact validation failed" in str(exc_info.value)


def test_coordinator_dual_loop_missing_packet_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-dual-loop-missing"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan\n\nstrategy: dual-loop\n", encoding="utf-8")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "Declared strategy 'dual-loop' requires artifact 'handoffs/task_packet_<task-id>.md'" in str(exc_info.value)


def test_gate1_manifest_required_when_strategy_graph(tmp_path):
    from control_plane.snapshot import SnapshotError
    repo = tmp_path / "repo"
    task_id = "task-graph-req"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan\n\nStrategy: graph\n", encoding="utf-8")

    with pytest.raises(SnapshotError) as exc_info:
        gate1_artifact_paths(repo, task_id, strategy="graph")
    assert "Strategy 'graph' requires canonical manifest" in str(exc_info.value)


def test_consumer_install_validator_resolution(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-consumer-val"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan\n\nstrategy: graph\n", encoding="utf-8")

    valid_manifest = {
        "schema_version": "1.0.0",
        "graph_id": "test-consumer-graph",
        "version": "1.0.0",
        "budget": {
            "token_ceiling_total": 50000,
            "max_parallel_concurrency": 4,
            "max_retries_per_node": 2,
        },
        "nodes": [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "deterministic_script",
                "command_or_eval": "echo read",
                "timeout_seconds": 30,
                "depends_on": [],
                "input_bindings": [],
                "output_contract": {},
                "failure_escalation": "rollback_and_halt",
            }
        ],
    }
    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text(json.dumps(valid_manifest), encoding="utf-8")

    # Install validator in consumer directory .agents/skills/graph-planner/scripts/validate_manifest.py
    consumer_script_dir = repo / ".agents" / "skills" / "graph-planner" / "scripts"
    consumer_script_dir.mkdir(parents=True, exist_ok=True)
    real_script = Path(__file__).resolve().parents[3] / "plugins" / "agent-orchestration" / "scripts" / "validate_manifest.py"
    shutil.copy2(real_script, consumer_script_dir / "validate_manifest.py")

    # Install schema in consumer directory .agents/skills/graph-planner/references/graph-manifest-schema.json
    consumer_ref_dir = repo / ".agents" / "skills" / "graph-planner" / "references"
    consumer_ref_dir.mkdir(parents=True, exist_ok=True)
    real_schema = Path(__file__).resolve().parents[3] / "plugins" / "agent-orchestration" / "references" / "graph-manifest-schema.json"
    shutil.copy2(real_schema, consumer_ref_dir / "graph-manifest-schema.json")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    receipt = coord._stage_plan_artifact_submission(task_id, task, template)
    assert receipt is not None
    assert receipt["gate_name"] == "plan_artifact_submission"


def test_coordinator_emits_runner_command_matching_parser_and_refuses_without_snapshot(tmp_path):
    import argparse
    repo = tmp_path / "repo"
    _setup_test_repo(repo)
    task_id = "task-emitted-cmd"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text('{"graph_id": "test"}', encoding="utf-8")
    signed_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    cp = MockControlPlane(repo)
    # 1. Insert real signed Gate 1 snapshot
    snapshot_json = json.dumps([{"label": "manifest", "sha256": signed_sha}])
    cp._conn.execute(
        "INSERT INTO transition_request (task_id, to_state, status, content_snapshot) VALUES (?, 'APPROVED', 'CONSUMED', ?)",
        (task_id, snapshot_json),
    )

    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._out = io.StringIO()
    coord._resolve_repo_root = lambda: repo
    coord._write_transition_guidance("APPROVED", "IN_WORKTREE", "post-transition", task_id=task_id)
    output = coord._out.getvalue()

    assert "- Execution Command (strategy: graph):" in output
    cmd_line = [l.strip() for l in output.splitlines() if l.strip().startswith("python3 ")][0]

    # Verify that the emitted command is valid according to graph_runner's argument parser
    runner_args = shlex.split(cmd_line)[2:]  # Skip 'python3' and script path

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--worktree")
    parser.add_argument("--approval", choices=["prompt", "none"])
    parser.add_argument("--expect-manifest-sha256")

    parsed = parser.parse_args(runner_args)
    assert parsed.manifest == f"docs/plans/work-tasks/{task_id}/{task_id}-graph-manifest.json"
    assert parsed.worktree == f".worktrees/{task_id}"
    assert parsed.approval == "none"
    assert parsed.expect_manifest_sha256 == signed_sha

    # 2. Refuse execution without signed snapshot in database
    cp._conn.execute("DELETE FROM transition_request")
    coord._out = io.StringIO()
    coord._write_transition_guidance("APPROVED", "IN_WORKTREE", "post-transition", task_id=task_id)
    output_no_snap = coord._out.getvalue()

    assert "Execution Command (strategy: graph)" not in output_no_snap
    assert "No cryptographically signed manifest snapshot found in Gate 1 approval. Execution command refused." in output_no_snap


def test_coordinator_dual_loop_with_manifest_only_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    _setup_test_repo(repo)
    task_id = "task-dual-manifest-only"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan", encoding="utf-8")

    # Only graph-manifest.json is present, but task explicitly declares dual-loop
    manifest_file = task_dir / f"{task_id}-graph-manifest.json"
    manifest_file.write_text('{"graph_id": "test"}', encoding="utf-8")

    # Task-scoped decision file explicitly chooses dual-loop
    dec_file = task_dir / f"{task_id}-strategy-decision.json"
    dec_file.write_text(json.dumps({"pattern": "dual-loop"}), encoding="utf-8")

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort())
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    # Must fail because task_packet is missing, even though graph-manifest is present!
    assert "requires artifact 'handoffs/task_packet_<task-id>.md'" in str(exc_info.value)


def test_transition_templates_patterns_parity():
    """Asserts exact pattern key parity between transition_templates.yaml and patterns.json."""
    import yaml

    repo_root = Path(__file__).resolve().parents[3]
    patterns_canonical = repo_root / "plugins" / "agent-orchestration" / "references" / "patterns.json"
    yaml_path = (
        repo_root
        / "plugins"
        / "agent-agentic-os"
        / "scripts"
        / "control_plane"
        / "transition_templates.yaml"
    )

    assert patterns_canonical.is_file(), f"Missing {patterns_canonical}"
    assert yaml_path.is_file(), f"Missing {yaml_path}"

    with open(patterns_canonical, "r", encoding="utf-8") as f:
        canon_data = json.load(f)

    with open(yaml_path, "r", encoding="utf-8") as f:
        y_data = yaml.safe_load(f)
    strat_arts = y_data.get("strategy_artifacts", {})

    assert set(canon_data.keys()) == set(strat_arts.keys()), (
        f"Mismatch between patterns.json ({set(canon_data.keys())}) "
        f"and transition_templates.yaml strategy_artifacts ({set(strat_arts.keys())})"
    )




