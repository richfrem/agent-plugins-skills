"""
tests/helpers/gate1_fixtures.py
===============================

Purpose:
    Shared setup for the Gate 1 (AWAITING_APPROVAL -> APPROVED) test files of
    auth-ciba-increment-b: walks a fresh task to AWAITING_APPROVAL through the real coordinator
    (the same sequence test_authorized_actor_enforcement.py uses; the older
    create_task_in_state helper predates the interview-outline gate).

Key Input Dependencies:
    - control_plane/pipeline_simulator.py, coordinator.py, registry.py

Key Functions:
    - reach_awaiting_approval(tmp_path, task_id) -> PipelineSimulator
"""

import io
from pathlib import Path

from control_plane.constants import STATE_AWAITING_APPROVAL
from control_plane.coordinator import TransitionCoordinator
from control_plane.pipeline_simulator import PipelineSimulator
from control_plane.registry import TransitionRegistry
from helpers.human_signer import get_test_human


def reach_awaiting_approval(tmp_path: Path, task_id: str) -> PipelineSimulator:
    """Walk a fresh task to AWAITING_APPROVAL through the real coordinator (the same
    sequence test_authorized_actor_enforcement uses; the older create_task_in_state
    helper predates the interview-outline gate)."""
    registry = TransitionRegistry.load_default()
    sim = PipelineSimulator(tmp_path / "control_plane.db", registry=registry)
    sim.create_task(task_id, "gate 1 setup")
    sim.control_plane.repo_root = tmp_path / "simulated-repo"
    sim.control_plane.repo_root.mkdir(parents=True, exist_ok=True)
    sim.enter_interview(task_id)
    sim.stage_interview_answers(task_id, classification="STANDARD", to_state="DRAFT_PLAN")
    sim.control_plane.record_plan_mode_entry(task_id, "simulator")
    sim.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD", expect_success=True)
    plan_dir = sim.control_plane.repo_root / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# spec", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# plan", encoding="utf-8")

    def step(answers, to_state, actor="human"):
        feed = iter(answers)
        TransitionCoordinator(
            sim.control_plane, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
        ).coordinate_transition(task_id=task_id, to_state=to_state, actor=actor, reason="gate 1 setup", interactive=True)

    step(["1", "YES"], "PLAN_REVIEW")
    step(["1", "3", "claude-cli", "test-model", "medium", "YES"], "MULTI_AGENT_REVIEW")  # internal method: runtime, model, effort are typed by the human
    sim.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "simulated review passed")
    step(["YES"], "PLAN_REVIEW", actor="simulator")
    step(["1", "YES"], STATE_AWAITING_APPROVAL)
    return sim


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
    """Walk a task through the real coordinator to WORKTREE_REVIEW with `worktree` (a git repo) registered.
    Earlier gates use the legacy default proof policy from tests/conftest.py (Gate 1 is not under test here)."""
    sim = reach_awaiting_approval(tmp_path, task_id)
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
    step(["YES"], "APPROVED")
    cp.record_human_approval(task_id, "simulator")
    cp.update_worktree(task_id, str(worktree), f"sim/{task_id}", "written_in_worktree")
    step(["YES"], "IN_WORKTREE", actor="simulator")
    cp.record_verification_receipt(task_id, "test_suite_deferred_to_review", "deferred", 0)
    step(["1", "1", "YES"], "WORKTREE_REVIEW")
    return sim


def reach_multi_agent_code_review(sim: PipelineSimulator, task_id: str) -> None:
    """WORKTREE_REVIEW -> MULTI_AGENT_CODE_REVIEW (internal method) plus a PASS critic outcome."""
    feed = iter(["1", "3", "claude-cli", "test-model", "medium", "YES"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
    ).coordinate_transition(task_id=task_id, to_state="MULTI_AGENT_CODE_REVIEW", actor="human", reason="gate 3 setup", interactive=True)
    sim.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "simulated review passed")
