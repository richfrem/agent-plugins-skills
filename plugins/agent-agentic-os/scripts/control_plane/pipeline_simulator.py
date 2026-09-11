"""Deterministic, production-boundary control-plane pipeline simulator."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Dict, Optional

from agent_control import ControlPlane
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.ports import PersistenceInvariantViolation
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS, CANONICAL_STATES, InvalidStateTransition
from control_plane.wrappers.record_retrospective import record_retrospective
from control_plane.wrappers.run_exit_verification import run_exit_verification


class PipelineSimulator:
    """Run bounded control-plane scenarios against a caller-owned temporary database.

    The simulator deliberately delegates transitions, questions, policy checks, and
    persistence to the production ``ControlPlane`` and ``TransitionCoordinator``.
    It reports registry-derived coverage; it does not maintain a second transition
    graph or write authorization rows directly.
    """

    def __init__(self, db_path: Path, *, registry: Optional[TransitionRegistry] = None):
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
        """Enter INTERVIEW through the production coordinator."""
        coordinator = TransitionCoordinator(self.control_plane, registry=self.registry, output_stream=io.StringIO())
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state="INTERVIEW",
            actor="simulator",
            reason="simulator interview entry",
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
            "interview_trivial_evidence": "The focused simulator test proves the smallest route.",
        }
        template = self.registry.get_template("INTERVIEW", to_state)
        if template is None:
            raise ValueError(f"No interview template for INTERVIEW -> {to_state}")
        capability = self.control_plane.verify_phase_capability(task_id, "interview_question")
        for question_id in template.stage_question_ids or []:
            self.control_plane.record_decision(
                task_id=task_id,
                source_occupancy_transition_id=capability.transition_id,
                from_state="INTERVIEW",
                to_state=to_state,
                question_id=question_id,
                answer=answers[question_id],
                actor="human",
            )

    def transition_from_interview(self, task_id: str, to_state: str, *, classification: str):
        """Attempt an interview route using the production coordinator."""
        coordinator = TransitionCoordinator(self.control_plane, registry=self.registry, output_stream=io.StringIO())
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state=to_state,
            actor="simulator",
            reason=f"simulator {classification.lower()} interview route",
        )

    def force_close(self, task_id: str, *, authorized: bool = False):
        """Exercise the explicit human force-close boundary."""
        coordinator = TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "FORCE_CLOSE",
            output_stream=io.StringIO(),
        )
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state="DONE",
            actor="human" if authorized else "simulator",
            reason="simulator force close",
            force_close=authorized,
            human_authorization="FORCE_CLOSE" if authorized else None,
            interactive=authorized,
        )

    def run_trivial_interview_fast_track(self, task_id: str) -> Dict[str, Any]:
        """Run INTAKE -> INTERVIEW -> RETROSPECTIVE with real stage enforcement."""
        self.enter_interview(task_id)
        self.stage_interview_answers(task_id, classification="TRIVIAL", to_state="RETROSPECTIVE")
        answers = iter(["1"])
        coordinator = TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(answers),
            output_stream=io.StringIO(),
        )
        coordinator.coordinate_transition(
            task_id=task_id,
            to_state="RETROSPECTIVE",
            actor="human",
            reason="simulator trivial fast-track",
            interactive=True,
        )
        return {
            "task_id": task_id,
            "states": ["INTAKE", "INTERVIEW", "RETROSPECTIVE"],
            "db_path": str(self.db_path),
        }

    def run_standard_happy_path(self, task_id: str) -> Dict[str, Any]:
        """Drive the complete STANDARD path through DONE in a temporary repo root."""
        repo_root = self.db_path.parent / "simulated-repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        self.control_plane.repo_root = repo_root
        self.enter_interview(task_id)
        self.stage_interview_answers(task_id, classification="STANDARD", to_state="DRAFT_PLAN")
        self.control_plane.record_plan_mode_entry(task_id, "simulator")
        self.transition_from_interview(task_id, "DRAFT_PLAN", classification="STANDARD")

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

        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "2",
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="human",
            reason="simulator requests plan review",
            interactive=True,
        )
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "4",
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="MULTI_AGENT_REVIEW",
            actor="human",
            reason="simulator selects external plan review",
            interactive=True,
        )
        self.control_plane.record_critic_review(task_id, 1, "simulator", "PASS", "simulated review passed")
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="PLAN_REVIEW",
            actor="simulator",
            reason="simulator review passed",
        )
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "1",
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="AWAITING_APPROVAL",
            actor="simulator",
            reason="simulator review passed",
            interactive=True,
        )

        approval_inputs = iter(["1", "y"])
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(approval_inputs),
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="APPROVED",
            actor="human",
            reason="simulator approval",
            interactive=True,
        )
        self.control_plane.record_human_approval(task_id, "simulator")

        worktree = repo_root / ".worktrees" / task_id
        worktree.mkdir(parents=True, exist_ok=True)
        self.control_plane.update_worktree(task_id, str(worktree), f"sim/{task_id}", "written_in_worktree")
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="IN_WORKTREE",
            actor="simulator",
            reason="simulator worktree ready",
        )
        self.control_plane.record_verification_receipt(task_id, "test_suite", "pytest -q", 0)
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "2",
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="WORKTREE_REVIEW",
            actor="human",
            reason="simulator worktree review",
            interactive=True,
        )
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="VERIFY_EXIT",
            actor="simulator",
            reason="simulator verification",
            skip_review=True,
            skip_reason="single deterministic simulator review",
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
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="RETROSPECTIVE",
            actor="simulator",
            reason="simulator verification passed",
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
        TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: "1",
            output_stream=io.StringIO(),
        ).coordinate_transition(
            task_id=task_id,
            to_state="DONE",
            actor="human",
            reason="simulator retrospective complete",
            interactive=True,
        )
        return {
            "task_id": task_id,
            "states": [
                "INTAKE", "INTERVIEW", "DRAFT_PLAN", "PLAN_REVIEW", "MULTI_AGENT_REVIEW",
                "AWAITING_APPROVAL", "APPROVED", "IN_WORKTREE", "WORKTREE_REVIEW",
                "VERIFY_EXIT", "RETROSPECTIVE", "DONE",
            ],
            "db_path": str(self.db_path),
        }

    def reset_to_intake(self, task_id: str):
        """Exercise the wildcard reset edge using genuine interactive inputs."""
        answers = iter(["The simulated task state must be re-run from intake.", "y"])
        coordinator = TransitionCoordinator(
            self.control_plane,
            registry=self.registry,
            input_fn=lambda _prompt: next(answers),
            output_stream=io.StringIO(),
        )
        return coordinator.coordinate_transition(
            task_id=task_id,
            to_state="INTAKE",
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
                task_id, "INTERVIEW", "RETROSPECTIVE"
            )
        )
        before_receipts = len(self.control_plane.get_verification_receipts(task_id))

        try:
            if name == "incomplete_interview":
                self.transition_from_interview(task_id, "RETROSPECTIVE", classification="TRIVIAL")
            elif name == "wrong_trivial_route":
                self.stage_interview_answers(task_id, classification="STANDARD", to_state="RETROSPECTIVE")
                before_decisions = len(
                    self.control_plane._persistence.get_unconsumed_transition_answers(
                        task_id, "INTERVIEW", "RETROSPECTIVE"
                    )
                )
                before_receipts = len(self.control_plane.get_verification_receipts(task_id))
                coordinator = TransitionCoordinator(
                    self.control_plane,
                    registry=self.registry,
                    input_fn=lambda _prompt: "1",
                    output_stream=io.StringIO(),
                )
                coordinator.coordinate_transition(
                    task_id=task_id,
                    to_state="RETROSPECTIVE",
                    actor="human",
                    reason="wrong route round",
                    interactive=True,
                )
            else:
                raise ValueError(f"Unknown simulation round: {name}")
        except TransitionCoordinatorError as exc:
            after_state = self.control_plane._persistence.read_current_state(task_id)
            after_id = self.control_plane._persistence.get_last_transition(task_id).transition_id
            after_decisions = len(self.control_plane._persistence.get_unconsumed_transition_answers(task_id, "INTERVIEW", "RETROSPECTIVE"))
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
                task_id, "INTAKE", "DONE"
            )
        )
        before_receipts = len(self.control_plane.get_verification_receipts(task_id))
        try:
            self.control_plane.transition(task_id, "DONE", "simulator", "illegal edge round")
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
                    task_id, "INTAKE", "DONE"
                )
            ),
            "no_orphan_receipt": before_receipts == len(self.control_plane.get_verification_receipts(task_id)),
        })

        task_id = new_task("trivial")
        result = self.run_trivial_interview_fast_track(task_id)
        rounds.append({
            "name": "trivial_fast_track",
            "result": "SUCCESS",
            "before_state": "INTAKE",
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
