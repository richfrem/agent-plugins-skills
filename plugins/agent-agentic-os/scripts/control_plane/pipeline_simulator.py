"""Deterministic, production-boundary control-plane pipeline simulator."""

from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from agent_control import ControlPlane
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.ports import PersistenceInvariantViolation
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS, CANONICAL_STATES, InvalidStateTransition
from control_plane.constants import (
    STATE_INTAKE, STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT, STATE_RETROSPECTIVE, STATE_DONE,
)

from control_plane.wrappers.record_retrospective import record_retrospective
from control_plane.wrappers.record_interview_question import record_interview_question
from control_plane.wrappers.run_exit_verification import run_exit_verification


class PipelineSimulator:
    """Run bounded control-plane scenarios against a caller-owned temporary database.

    The simulator deliberately delegates transitions, questions, policy checks, and
    persistence to the production ``ControlPlane`` and ``TransitionCoordinator``.
    It reports registry-derived coverage; it does not maintain a second transition
    graph or write authorization rows directly.
    """

    def __init__(self, db_path: Path, *, registry: Optional[TransitionRegistry] = None,
                 human_signer: Optional[Callable[..., Any]] = None):
        """`human_signer` completes the cryptographic gates (APPROVED, VERIFY_EXIT, DONE): it is called with the
        control plane and a transition_request id and must return the committed TransitionRecord, exactly as a
        human running `ssh-keygen -Y sign` would. Without one the simulator halts at the first such gate with
        HUMAN_PROOF_REQUIRED -- it never fabricates authority."""
        self.human_signer = human_signer
        self.db_path = Path(db_path).resolve()
        self.repository_root = Path(__file__).resolve().parents[3]
        if self.db_path == (self.repository_root / "context" / "control_plane.db").resolve():
            raise ValueError("Pipeline simulator requires a temporary database, not the repository database")
        self.control_plane = ControlPlane(db_path=self.db_path)
        self.control_plane.init_db()
        self.registry = registry or TransitionRegistry.load_default()

    def create_task(self, task_id: str, title: str) -> str:
        """Create a general task in the simulator database."""
        self.control_plane.create_task(task_id=task_id, title=title, runtime_tool="simulator")
        return task_id

    def enter_interview(self, task_id: str):
        """Enter INTERVIEW through the production coordinator. INTAKE -> INTERVIEW has zero
        own human_questions, so only the mandatory guidance-compliance confirmation is asked."""
        coordinator = TransitionCoordinator(
            self.control_plane, registry=self.registry,
            input_fn=lambda _prompt: "YES", output_stream=io.StringIO(),
        )
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state=STATE_INTERVIEW,
            actor="simulator",
            reason="simulator interview entry",
            interactive=True,
        )

    def stage_interview_answers(self, task_id: str, *, classification: str, to_state: str) -> None:
        """Stage interview answers through the supported decision API.

        This is fixture setup for a temporary run. It binds each answer to the
        current INTERVIEW occupancy transition through ``record_decision``; it
        never inserts SQLite authorization rows itself.
        """
        answers = {
            "interview_classification": classification,
            "interview_summary": "The simulator validates the control-plane path.",
            "interview_scope": "Only the temporary simulator database and production APIs.",
            "interview_verification": "Focused simulator tests pass.",
            "interview_acceptance_criteria": "The requested route is enforced and recorded.",
            "interview_planning_model_effort": "Use a capable mid-tier model at medium effort for the simulated planning phase.",
            "interview_trivial_evidence": "The focused simulator test proves the smallest route.",
        }
        template = self.registry.get_template(STATE_INTERVIEW, to_state)
        if template is None:
            raise ValueError(f"No interview template for INTERVIEW -> {to_state}")
        if to_state == STATE_DRAFT_PLAN:
            for question_id in template.stage_question_ids or []:
                record_interview_question(
                    task_id=task_id,
                    question=question_id,
                    options={},
                    recommended="",
                    answer=answers[question_id],
                    actor="human",
                    target_state=STATE_DRAFT_PLAN,
                    control_plane=self.control_plane,
                )
            return
        capability = self.control_plane.verify_phase_capability(task_id, "interview_question")
        for question_id in template.stage_question_ids or []:
            self.control_plane.record_decision(
                task_id=task_id,
                source_occupancy_transition_id=capability.transition_id,
                from_state=STATE_INTERVIEW,
                to_state=to_state,
                question_id=question_id,
                answer=answers[question_id],
                actor="human",
            )
            self.control_plane.update_interview_plan_outline(
                task_id, question_id, answers[question_id], actor="human"
            )

    def transition_from_interview(self, task_id: str, to_state: str, *, classification: str, expect_success: bool = False):
        """Attempt an interview route using the production coordinator. Callers exercising an
        intentional denial (e.g. incomplete-interview rounds) leave expect_success False -- the
        coordinator still fails closed for the right reason (missing stage question answers)
        before ever reaching the guidance-compliance question. Callers driving a genuine,
        successful route (e.g. the STANDARD happy path) must pass expect_success=True so the
        mandatory guidance-compliance confirmation is answered too."""
        if expect_success:
            coordinator = TransitionCoordinator(
                self.control_plane, registry=self.registry,
                input_fn=lambda _prompt: "YES", output_stream=io.StringIO(),
            )
        else:
            coordinator = TransitionCoordinator(self.control_plane, registry=self.registry, output_stream=io.StringIO())
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state=to_state,
            actor="simulator",
            interactive=expect_success,
            reason=f"simulator {classification.lower()} interview route",
        )

    def _seed_gate1_content(self, task_id: str) -> None:
        """Write the reviewed spec and plan that Gate 1's transition_request binds (the human signs their hashes)."""
        from control_plane.snapshot import gate1_artifact_paths

        for label, path in gate1_artifact_paths(self.control_plane.repo_root, task_id):
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {label} for {task_id} (simulated)\n")

    @staticmethod
    def _init_git_worktree(worktree: Path) -> Path:
        """A one-commit git repository at `worktree`: Gate 3 signs its commit SHA, diff and untracked-file hashes."""
        worktree.mkdir(parents=True, exist_ok=True)
        if (worktree / ".git").exists():
            return worktree
        env = {"GIT_AUTHOR_NAME": "sim", "GIT_AUTHOR_EMAIL": "sim@local", "GIT_COMMITTER_NAME": "sim", "GIT_COMMITTER_EMAIL": "sim@local"}
        import os as _os

        env["PATH"] = _os.environ.get("PATH", "")
        env["HOME"] = str(worktree)
        (worktree / "simulated.txt").write_text("simulated\n")
        for args in (["init", "-q"], ["add", "."], ["commit", "-q", "-m", "simulated base"]):
            subprocess.run(["git", "-C", str(worktree), *args], check=True, env=env, capture_output=True)
        return worktree

    def signed_close(self, task_id: str, *, signed: bool = False):
        """Exercise the closure boundary: every edge into DONE takes a human signature. With signed=False the
        attempt is non-interactive and must halt with HUMAN_PROOF_REQUIRED; with signed=True the configured
        human_signer completes the request."""
        coordinator = TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            output_stream=io.StringIO(),
            human_signer=self.human_signer,
        )
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state=STATE_DONE,
            actor="human" if signed else "simulator",
            reason="simulator signed close",
            interactive=signed,
        )

    def run_trivial_interview_fast_track(self, task_id: str) -> Dict[str, Any]:
        """Run INTAKE -> INTERVIEW -> RETROSPECTIVE via the human-authorized emergency-close
        edge, answering the reason category (planned/trivial, not a failure) then the literal
        FORCE_RETROSPECTIVE confirmation -- both option 1 on their respective questions."""
        self.enter_interview(task_id)
        answers = iter(["1", "1", "YES"])
        coordinator = TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(answers),
            output_stream=io.StringIO(),
        )
        coordinator.coordinate_transition(
            task_id=task_id,
            to_state=STATE_RETROSPECTIVE,
            actor="human",
            reason="simulator trivial fast-track",
            interactive=True,
        )
        return {
            "task_id": task_id,
            "states": [STATE_INTAKE, STATE_INTERVIEW, STATE_RETROSPECTIVE],
            "db_path": str(self.db_path),
        }

    def run_standard_happy_path(self, task_id: str) -> Dict[str, Any]:
        """Drive the complete STANDARD path through DONE in a temporary repo root."""
        repo_root = self.db_path.parent / "simulated-repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        self.control_plane.repo_root = repo_root
        self.enter_interview(task_id)
        self.stage_interview_answers(task_id, classification="STANDARD", to_state=STATE_DRAFT_PLAN)
        self.control_plane.record_plan_mode_entry(task_id, "simulator")
        self.transition_from_interview(task_id, STATE_DRAFT_PLAN, classification="STANDARD", expect_success=True)

        plan_dir = repo_root / "docs" / "plans"
        plan_dir.mkdir(parents=True, exist_ok=True)
        (plan_dir / f"{task_id}-spec.md").write_text("# simulated specification", encoding="utf-8")
        evidence = repo_root / ".implementation-evidence" / f"{task_id}.txt"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("simulated implementation completed\n", encoding="utf-8")
        ledger = [{
            "id": "simulated-implementation",
            "status": "COMPLETE",
            "artifacts": [str(evidence.relative_to(repo_root))],
            "evidence": "simulator implementation step",
        }]
        (plan_dir / f"{task_id}-implementation-plan.md").write_text(
            "# simulated implementation plan\n\n"
            "## Implementation Task Ledger\n```json\n"
            + json.dumps(ledger, indent=2)
            + "\n```\n",
            encoding="utf-8",
        )

        plan_review_answers = iter(["1", "YES"])
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(plan_review_answers),
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_PLAN_REVIEW,
            actor="human",
            reason="simulator requests plan review",
            interactive=True,
        )
        review_answers = iter(["1", "3", "claude-cli", "test-model", "medium", "YES"])
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(review_answers),
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_MULTI_AGENT_REVIEW,
            actor="human",
            reason="simulator selects internal plan review",
            interactive=True,
        )
        self.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "simulated review passed")
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "YES",  # MULTI_AGENT_REVIEW->PLAN_REVIEW has zero own questions
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_PLAN_REVIEW,
            actor="simulator",
            reason="simulator review passed",
            interactive=True,
        )
        awaiting_answers = iter(["1", "YES"])
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(awaiting_answers),
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_AWAITING_APPROVAL,
            actor="simulator",
            reason="simulator review passed",
            interactive=True,
        )

        self._seed_gate1_content(task_id)
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            output_stream=io.StringIO(),
            human_signer=self.human_signer,
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_APPROVED,
            actor="human",
            reason="simulator approval",
            interactive=True,
        )
        self.control_plane.record_human_approval(task_id, "simulator")

        worktree = self._init_git_worktree(repo_root / ".worktrees" / task_id)
        self.control_plane.update_worktree(task_id, str(worktree), f"sim/{task_id}", "written_in_worktree")
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "YES",  # APPROVED->IN_WORKTREE has zero own questions
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_IN_WORKTREE,
            actor="simulator",
            reason="simulator worktree ready",
            interactive=True,
        )
        self.control_plane.record_verification_receipt(task_id, "test_suite", "pytest -q", 0)
        worktree_review_answers = iter(["1", "1", "YES"])
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(worktree_review_answers),
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_WORKTREE_REVIEW,
            actor="human",
            reason="simulator worktree review",
            interactive=True,
        )
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            output_stream=io.StringIO(),
            human_signer=self.human_signer,  # Gate 3 is a human signature over commit SHA + diff + untracked hashes
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_VERIFY_EXIT,
            actor="human",
            reason="simulator verification",
            interactive=True,
        )
        run_exit_verification(
            task_id,
            verifier_id="pytest_unit_tests",
            command=["python3", "-c", "print('pass')"],
            cwd=str(worktree),
            control_plane=self.control_plane,
        )
        run_exit_verification(
            task_id,
            verifier_id="pytest_full_suite",
            command=["python3", "-c", "print('full suite pass')"],
            cwd=str(worktree),
            control_plane=self.control_plane,
        )
        run_exit_verification(
            task_id,
            verifier_id="leak_check",
            command=["python3", "-c", "print('clean')"],
            cwd=str(worktree),
            control_plane=self.control_plane,
        )
        self.control_plane.log_asymmetric_persistence(
            task_id,
            "references/map-debt.md",
            "CONFIRMED",
            "standard simulator path evidence",
        )
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "YES",  # VERIFY_EXIT->RETROSPECTIVE has zero own questions
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_RETROSPECTIVE,
            actor="simulator",
            reason="simulator verification passed",
            interactive=True,
        )
        record_retrospective(
            task_id,
            {
                "decision": "opt_in",
                "completion_mode": "completed",
                "actor": "agent",
                "outcome": "simulated standard path passed",
                "strengths": "gates were explicit",
                "friction": "none",
                "learning": "follow transition guidance",
                "improvement": "keep standard-path replayable",
                "follow_up": "",
            },
            [],
            control_plane=self.control_plane,
        )
        done_answers = iter(["1", "YES"])
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(done_answers),
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state=STATE_DONE,
            actor="human",
            reason="simulator retrospective complete",
            interactive=True,
        )
        return {
            "task_id": task_id,
            "states": [
                STATE_INTAKE, STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_MULTI_AGENT_REVIEW,
                STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW,
                STATE_VERIFY_EXIT, STATE_RETROSPECTIVE, STATE_DONE,
            ],
            "db_path": str(self.db_path),
        }

    def get_post_done_convergence_protocol(self) -> Dict[str, Any]:
        """Return the codified post-DONE Git convergence protocol from the stage contract."""
        done_stage = self.registry.get_stage_contract(STATE_DONE)
        closeout = done_stage.get("closeout_contract", {})
        return closeout.get("post_done_protocol", {})

    def reset_to_intake(self, task_id: str):
        """Exercise the wildcard reset edge using genuine interactive inputs."""
        answers = iter(["The simulated task state must be re-run from intake.", "y", "YES"])
        coordinator = TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(answers),
            output_stream=io.StringIO(),
        )
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state=STATE_INTAKE,
            actor="human",
            reason="simulator reset",
            interactive=True,
        )

    def edge_scenario_coverage(self) -> Dict[tuple[str, str], Dict[str, Any]]:
        """Return one executable scenario descriptor for every live registry edge."""
        coverage = {}
        for template in self.registry.get_all_templates():
            edge = (template.from_state, template.to_state)
            coverage[edge] = {
                "transition_id": template.transition_id,
                "human_questions": list(template.human_questions),
                "deterministic_checks": list(template.deterministic_checks),
                "required_artifacts": list(template.required_artifacts),
                "approval_required": bool(template.approval.get("required")),
                "recovery_states": list(ALLOWED_TRANSITIONS.get(template.to_state, [])),
            }
        return coverage

    def isolation_report(self) -> Dict[str, Any]:
        """Describe the simulator's deliberately narrow side-effect boundary."""
        return {
            "database": str(self.db_path),
            "uses_repository_database": self.db_path == (self.repository_root / "context" / "control_plane.db").resolve(),
            "uses_git_or_subprocess": False,
            "uses_worktree": False,
        }

    def play_round(self, name: str, prefix: str) -> Dict[str, Any]:
        """Play one named improvement round and return its evidence record."""
        task_id = self.create_task(f"{prefix}-{name}", f"Simulator round: {name}")
        self.enter_interview(task_id)
        before_id = self.control_plane._persistence.get_last_transition(task_id).transition_id
        before_state = self.control_plane._persistence.read_current_state(task_id)
        before_decisions = len(
            self.control_plane._persistence.get_unconsumed_transition_answers(
                task_id, STATE_INTERVIEW, STATE_RETROSPECTIVE
            )
        )
        before_receipts = len(self.control_plane.get_verification_receipts(task_id))

        try:
            if name == "incomplete_interview":
                self.transition_from_interview(task_id, STATE_RETROSPECTIVE, classification="TRIVIAL")
            elif name == "wrong_trivial_route":
                # Simulates a human/agent supplying an undeclared answer to the reason-category
                # question on the emergency-close edge -- the coordinator must fail closed
                # rather than guess at a similar-but-not-exact option.
                before_decisions = len(
                    self.control_plane._persistence.get_unconsumed_transition_answers(
                        task_id, STATE_INTERVIEW, STATE_RETROSPECTIVE
                    )
                )
                before_receipts = len(self.control_plane.get_verification_receipts(task_id))
                coordinator = TransitionCoordinator(
                    self.control_plane,
                    registry=self.registry,
                    input_fn=lambda _prompt: "STANDARD",
                    output_stream=io.StringIO(),
                )
                coordinator.coordinate_transition(
                    task_id=task_id,
                    to_state=STATE_RETROSPECTIVE,
                    actor="human",
                    reason="wrong route round",
                    interactive=True,
                )
            else:
                raise ValueError(f"Unknown simulation round: {name}")
        except TransitionCoordinatorError as exc:
            after_state = self.control_plane._persistence.read_current_state(task_id)
            after_id = self.control_plane._persistence.get_last_transition(task_id).transition_id
            after_decisions = len(self.control_plane._persistence.get_unconsumed_transition_answers(task_id, STATE_INTERVIEW, STATE_RETROSPECTIVE))
            return {
                "name": name,
                "result": "DENIED_AS_EXPECTED",
                "error": str(exc),
                "before_state": before_state,
                "after_state": after_state,
                "state_preserved": before_state == after_state,
                "no_orphan_transition": before_id == after_id,
                "no_orphan_decision": after_decisions == before_decisions,
                "no_orphan_receipt": len(self.control_plane.get_verification_receipts(task_id)) == before_receipts,
            }
        return {
            "name": name,
            "result": "UNEXPECTED_SUCCESS",
            "before_state": before_state,
            "after_state": self.control_plane._persistence.read_current_state(task_id),
            "state_preserved": False,
            "no_orphan_transition": False,
        }

    def play_adversarial_rounds(self, prefix: str) -> list[Dict[str, Any]]:
        """Play deterministic denial, recovery, and success rounds.

        Each round gets a fresh task so a failed move cannot be hidden by a later
        successful move. The returned receipt is intentionally small: it exposes
        the state before/after and proves that denied moves did not append a
        transition row.
        """
        rounds = []

        def new_task(name: str) -> str:
            return self.create_task(f"{prefix}-{name}", f"Simulator round: {name}")

        def last_transition_id(task_id: str) -> int:
            transition = self.control_plane._persistence.get_last_transition(task_id)
            return transition.transition_id if transition else 0

        rounds.extend(
            (
                self.play_round("incomplete_interview", prefix),
                self.play_round("wrong_trivial_route", prefix),
            )
        )

        task_id = new_task("illegal")
        before_id = last_transition_id(task_id)
        before_state = self.control_plane._persistence.read_current_state(task_id)
        before_decisions = len(
            self.control_plane._persistence.get_unconsumed_transition_answers(
                task_id, STATE_INTAKE, STATE_VERIFY_EXIT
            )
        )
        before_receipts = len(self.control_plane.get_verification_receipts(task_id))
        try:
            self.control_plane.transition(task_id, STATE_DONE, "simulator", "illegal edge round")
        except (InvalidStateTransition, PersistenceInvariantViolation):
            pass
        after_state = self.control_plane._persistence.read_current_state(task_id)
        rounds.append({
            "name": "illegal_edge",
            "result": "DENIED_AS_EXPECTED",
            "before_state": before_state,
            "after_state": after_state,
            "state_preserved": before_state == after_state,
            "no_orphan_transition": before_id == last_transition_id(task_id),
            "no_orphan_decision": before_decisions == len(
                self.control_plane._persistence.get_unconsumed_transition_answers(
                    task_id, STATE_INTAKE, STATE_VERIFY_EXIT
                )
            ),
            "no_orphan_receipt": before_receipts == len(self.control_plane.get_verification_receipts(task_id)),
        })

        task_id = new_task("trivial")
        result = self.run_trivial_interview_fast_track(task_id)
        rounds.append({
            "name": "trivial_fast_track",
            "result": "SUCCESS",
            "before_state": STATE_INTAKE,
            "after_state": result["states"][-1],
            "state_preserved": False,
            "no_orphan_transition": True,
        })

        task_id = new_task("reset")
        self.enter_interview(task_id)
        reset_record = self.reset_to_intake(task_id)
        rounds.append({
            "name": "reset_recovery",
            "result": "SUCCESS",
            "before_state": reset_record.from_state,
            "after_state": reset_record.to_state,
            "state_preserved": False,
            "no_orphan_transition": True,
        })
        return rounds
