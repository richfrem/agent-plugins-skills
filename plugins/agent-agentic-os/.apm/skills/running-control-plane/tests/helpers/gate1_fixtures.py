"""
tests/helpers/gate1_fixtures.py
===============================

Purpose:
    Shared setup for the Gate 1 (PLAN_REVIEW -> APPROVED) and Gate 3
    (WORKTREE_REVIEW -> VERIFY_EXIT) test files: walks a fresh task to
    PLAN_REVIEW (or WORKTREE_REVIEW) through the real coordinator using the
    lean 10-state schema v15 machine.

Key Input Dependencies:
    - control_plane/pipeline_simulator.py, coordinator.py, registry.py

Key Functions:
    - reach_plan_review(tmp_path, task_id) -> PipelineSimulator
    - reach_awaiting_approval(tmp_path, task_id) -> PipelineSimulator (compat alias)
    - reach_worktree_review(tmp_path, task_id, worktree) -> PipelineSimulator
    - reach_multi_agent_code_review(sim, task_id) -> None (compat shim; records critic PASS in WORKTREE_REVIEW)
"""

import io
from pathlib import Path

from control_plane.constants import STATE_DRAFT_PLAN, STATE_PLAN_REVIEW
from control_plane.coordinator import TransitionCoordinator
from control_plane.pipeline_simulator import PipelineSimulator
from control_plane.registry import TransitionRegistry
from helpers.human_signer import get_test_human


def reach_plan_review(tmp_path: Path, task_id: str) -> PipelineSimulator:
    """Walk a fresh task to PLAN_REVIEW (Gate 1 source state in schema v15) through the real coordinator."""
    registry = TransitionRegistry.load_default()
    sim = PipelineSimulator(tmp_path / "control_plane.db", registry=registry)
    sim.create_task(task_id, "gate 1 setup")
    sim.control_plane.repo_root = tmp_path / "simulated-repo"
    sim.control_plane.repo_root.mkdir(parents=True, exist_ok=True)

    def step(answers, to_state, actor="human"):
        feed = iter(answers)
        TransitionCoordinator(
            sim.control_plane, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
        ).coordinate_transition(task_id=task_id, to_state=to_state, actor=actor, reason="gate 1 setup", interactive=True)

    # INTAKE -> DRAFT_PLAN (1 question: intake_outline_confirmed)
    step(["1"], STATE_DRAFT_PLAN)
    plan_dir = sim.control_plane.repo_root / "docs" / "plans" / "work-tasks" / task_id
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# spec\n", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# plan\n\n- Strategy: direct\n", encoding="utf-8")

    # DRAFT_PLAN -> PLAN_REVIEW (agent_or_human, 0 questions)
    step([], STATE_PLAN_REVIEW, actor="simulator")
    return sim


# Compatibility alias for tests written before schema v15 collapsed AWAITING_APPROVAL into PLAN_REVIEW.
reach_awaiting_approval = reach_plan_review


def init_git_worktree(directory: Path) -> Path:
    """A real git repository with one commit, used as the registered worktree for Gate 3 tests."""
    import subprocess

    directory.mkdir(parents=True, exist_ok=True)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "PATH": __import__("os").environ["PATH"], "HOME": str(directory)}
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(directory)] + args, check=True, env=env, capture_output=True)
    (directory / "module.py").write_text("VALUE = 1\n")
    subprocess.run(["git", "-C", str(directory), "add", "."], check=True, env=env, capture_output=True)
    subprocess.run(["git", "-C", str(directory), "commit", "-q", "-m", "base"], check=True, env=env, capture_output=True)
    return directory


def reach_worktree_review(tmp_path: Path, task_id: str, worktree: Path) -> PipelineSimulator:
    """Walk a task through the real coordinator to WORKTREE_REVIEW with `worktree` (a git repo) registered."""
    sim = reach_plan_review(tmp_path, task_id)
    cp = sim.control_plane

    def step(answers, to_state, actor="human"):
        feed = iter(answers)
        TransitionCoordinator(
            cp, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
            human_signer=get_test_human().sign_request,  # setup signs for real, even in tests that assert the strict halt
        ).coordinate_transition(task_id=task_id, to_state=to_state, actor=actor, reason="gate 3 setup", interactive=True)

    folder = Path(cp.repo_root) / "docs" / "plans" / "work-tasks" / task_id  # what the human signs at Gate 1
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{task_id}-spec.md").write_text("spec v1\n")
    (folder / f"{task_id}-implementation-plan.md").write_text("plan v1\n")
    step([], "APPROVED")
    cp.record_human_approval(task_id, "simulator")
    cp.update_worktree(task_id, str(worktree), f"sim/{task_id}", "written_in_worktree")
    step([], "IN_WORKTREE", actor="simulator")
    cp.record_verification_receipt(task_id, "test_suite_deferred_to_review", "deferred", 0)
    step([], "WORKTREE_REVIEW", actor="simulator")
    return sim


def reach_multi_agent_code_review(sim: PipelineSimulator, task_id: str) -> None:
    """Schema v15 compat shim: code review runs inside WORKTREE_REVIEW; record a PASS critic outcome."""
    sim.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "simulated review passed")
