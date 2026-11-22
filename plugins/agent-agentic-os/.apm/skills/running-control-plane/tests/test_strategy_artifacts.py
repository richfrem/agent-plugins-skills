"""
test_strategy_artifacts.py — Test Data-Driven Strategy Artifacts and Manifest Binding (PR B)
=============================================================================================

Validates:
1. Strategies come from the sibling orchestrating-agent-work's patterns.json; the YAML strategy_artifacts keeps
   only the control-plane-owned triple-loop-learning (S1, B11/B12).
2. TransitionCoordinator detects declared strategy and validates strategy-specific plan artifacts.
3. If declared strategy is 'graph', graph-manifest.json is required and validated via validate_manifest.py.
4. If manifest validation fails, transition to PLAN_REVIEW is rejected with clear diagnostics.
5. If validator script is missing, coordinator fails closed.
6. Gate 1 content snapshot binds graph-manifest.json when present for the task.

The coordinator is given a fixture skills root (helpers/orchestration_fixture.py) shaped like an APM install;
the source tree is never a runtime location (spec G6, B9).
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
from control_plane import orchestration_registry
from helpers.orchestration_fixture import ORCHESTRATION_SKILLS_SOURCE, make_skills_root

VALID_GRAPH_MANIFEST = {
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


def test_registry_loads_strategy_artifacts(tmp_path):
    # S1 (B11/B12): graph, dual-loop, agent-swarm and direct moved to the single registry (patterns.json in the
    # sibling orchestrating-agent-work); the YAML keeps only triple-loop-learning. Same checks, new owner.
    registry = TransitionRegistry.load_default()
    assert set(registry.strategy_artifacts) == {"triple-loop-learning"}
    root = make_skills_root(tmp_path)
    for name in ("graph", "dual-loop", "agent-swarm", "direct"):
        assert orchestration_registry.strategy_config(name, root, registry) is not None

    graph_cfg = orchestration_registry.strategy_config("graph", root, registry)
    assert graph_cfg is not None
    assert "graph-manifest.json" in graph_cfg["plan_artifact"]
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


def _setup_test_repo(repo: Path) -> Path:
    """Create the repo folder and return a fixture skills root holding the orchestration siblings (B9: the old
    `plugins/agent-orchestration` symlink pointed at a pre-APM path and dangled)."""
    repo.mkdir(parents=True, exist_ok=True)
    return make_skills_root(repo.parent)


def test_coordinator_graph_strategy_validates_and_stages_manifest(tmp_path):
    repo = tmp_path / "repo"
    skills = _setup_test_repo(repo)
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
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    receipt = coord._stage_plan_artifact_submission(task_id, task, template)
    assert receipt is not None
    assert receipt["gate_name"] == "plan_artifact_submission"
    assert f"graph:{task_id}-graph-manifest.json=" in receipt["command_executed"]


def test_coordinator_graph_strategy_missing_manifest_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    skills = _setup_test_repo(repo)
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
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "Declared strategy 'graph' requires artifact" in str(exc_info.value)


def test_coordinator_graph_strategy_invalid_manifest_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    skills = _setup_test_repo(repo)
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
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
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

    # The installed orchestrating-agent-work sibling has no validator script (B8: no folder search any more).
    skills = make_skills_root(tmp_path, skills=())
    partial = skills / "orchestrating-agent-work"
    (partial / "references").mkdir(parents=True)
    (partial / "SKILL.md").write_text("---\nname: orchestrating-agent-work\n---\n", encoding="utf-8")
    shutil.copy2(ORCHESTRATION_SKILLS_SOURCE / "orchestrating-agent-work" / "references" / "patterns.json",
                 partial / "references" / "patterns.json")
    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    # message text changed with the APM-sibling resolution (S1): it names the missing validator and the install
    assert "validate_manifest.py is not installed beside running-control-plane" in str(exc_info.value)
    assert "apm install richfrem/agent-plugins-skills/plugins/agent-orchestration" in str(exc_info.value)


def test_coordinator_unknown_strategy_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-unknown-strat"
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    spec_file = task_dir / f"{task_id}-spec.md"
    plan_file = task_dir / f"{task_id}-implementation-plan.md"
    spec_file.write_text("# Spec", encoding="utf-8")
    plan_file.write_text("# Plan\n\nstrategy: grahp\n", encoding="utf-8")

    skills = make_skills_root(tmp_path)
    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    assert "Declared execution strategy 'grahp' is unknown or not supported" in str(exc_info.value)


def test_coordinator_rollback_strategy_revert_not_treated_as_strategy(tmp_path):
    repo = tmp_path / "repo"
    skills = _setup_test_repo(repo)
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
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
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

    skills = make_skills_root(tmp_path)
    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
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

    # A consumer install (S1, B8): APM copies the orchestrating-agent-work skill beside running-control-plane in the
    # consumer's skills folder (not the retired .agents/skills/graph-planner layout). Real copies, not symlinks, so the
    # validator and its schema resolve from the installed copy and never from this source tree.
    skills = tmp_path / "consumer-home" / ".claude" / "skills"
    installed = skills / "orchestrating-agent-work"
    source = ORCHESTRATION_SKILLS_SOURCE / "orchestrating-agent-work"
    for rel in ("SKILL.md", "references/patterns.json", "references/graph-manifest-schema.json", "scripts/validate_manifest.py"):
        (installed / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, installed / rel)

    cp = MockControlPlane(repo)
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    receipt = coord._stage_plan_artifact_submission(task_id, task, template)
    assert receipt is not None
    assert receipt["gate_name"] == "plan_artifact_submission"


def test_coordinator_emits_runner_command_matching_parser_and_refuses_without_snapshot(tmp_path):
    import argparse
    repo = tmp_path / "repo"
    skills = _setup_test_repo(repo)
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

    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
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
    skills = _setup_test_repo(repo)
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
    coord = TransitionCoordinator(cp, fs=MockFilesystemPort(), skills_root=skills)
    coord._resolve_repo_root = lambda: repo
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")

    task = {"task_id": task_id}
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, task, template)
    # Must fail because task_packet is missing, even though graph-manifest is present!
    assert "requires artifact 'handoffs/task_packet_<task-id>.md'" in str(exc_info.value)


def test_transition_templates_patterns_parity():
    """S1 (B11/B12) replaces "two registries with equal keys" by ONE registry: patterns.json owns every
    orchestration strategy, the YAML owns only triple-loop-learning, no key is in both, and together they cover
    exactly the strategies the orchestration skill documents (PATTERN_GUIDE.md section 6, plus direct).
    Paths fixed from the pre-APM layout (B9)."""
    import yaml

    patterns_canonical = ORCHESTRATION_SKILLS_SOURCE / "orchestrating-agent-work" / "references" / "patterns.json"
    yaml_path = Path(orchestration_registry.__file__).resolve().parent / "transition_templates.yaml"

    assert patterns_canonical.is_file(), f"Missing {patterns_canonical}"
    assert yaml_path.is_file(), f"Missing {yaml_path}"

    with open(patterns_canonical, "r", encoding="utf-8") as f:
        canon_data = json.load(f)

    with open(yaml_path, "r", encoding="utf-8") as f:
        y_data = yaml.safe_load(f)
    strat_arts = y_data.get("strategy_artifacts", {})

    assert not set(canon_data) & set(strat_arts), (
        f"Strategy registered twice: patterns.json and transition_templates.yaml both list {set(canon_data) & set(strat_arts)}"
    )
    assert set(strat_arts) == {"triple-loop-learning"}
    assert set(canon_data) | set(strat_arts) == {
        "direct", "dual-loop", "graph", "agent-swarm", "red-team-review", "learning-loop", "triple-loop-learning",
    }




