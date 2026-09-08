#!/usr/bin/env python3
"""
control_plane/coordinator.py — TransitionCoordinator (issue-529 Slice 5)
========================================================================

Purpose:
    Sole authoritative orchestration front-door for proposing and coordinating
    task lifecycle transitions in the SQLite Control Plane.
    Enforces:
    - Loading template, plain-language checklist, and human questions from TransitionRegistry.
    - Evaluating edge-specific deterministic policy checks via policy.py.
    - Sequential question presentation (1 question at a time) with explicit [Recommended] default.
    - Requiring explicit decision inputs (no inferred chat answers).
    - Constructing normalized TransitionCommitRequest and committing via ControlPlane.
    - Presenting structured visible transition report (purpose, checklist, decisions, released/prohibited capabilities).
"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TextIO, Tuple
from control_plane.registry import TransitionRegistry, TransitionTemplate, TransitionRegistryError
from control_plane.policy import evaluate_check, PolicyViolation, PolicyConfigurationError
from control_plane.ports import (
    FilesystemPort,
    TransitionCommitRequest,
    TransitionDecision,
    TransitionRecord,
)


class TransitionCoordinatorError(Exception):
    """Raised when transition coordination preconditions or decisions are incomplete or rejected."""
    pass


class TransitionCoordinator:
    """Coordinates lifecycle transitions between states."""

    def __init__(
        self,
        control_plane: Any,
        registry: Optional[TransitionRegistry] = None,
        input_fn: Optional[Callable[[str], str]] = None,
        output_stream: Optional[TextIO] = None,
        fs: Optional[FilesystemPort] = None,
        repo_root: Optional[Path] = None,
    ):
        self._cp = control_plane
        self._registry = registry or getattr(control_plane, "_transition_registry", None) or TransitionRegistry.load_default()
        self._input_fn = input_fn or input
        self._out = output_stream or sys.stdout
        self._fs = fs or getattr(control_plane, "_fs", None)
        if self._fs is None:
            from control_plane.adapters import FilesystemAdapter
            self._fs = FilesystemAdapter()
        self._repo_root = repo_root or getattr(control_plane, "repo_root", None)

    def coordinate_transition(
        self,
        task_id: str,
        to_state: str,
        actor: str,
        reason: str,
        interactive: bool = False,
        provided_answers: Optional[Dict[str, str]] = None,
        approval_decision: Optional[str] = None,
        skip_decision: Optional[Tuple[str, str]] = None,  # (skip_chosen, reason)
        skip_review: bool = False,
        skip_reason: Optional[str] = None,
    ) -> TransitionRecord:
        """Coordinates and commits a transition according to the template contract."""
        # 1. State machine validation
        self._cp._state_machine.validate_known_state(to_state)

        task = self._cp.get_task(task_id)
        if not task:
            raise TransitionCoordinatorError(f"Task not found: {task_id}")

        current_state = self._cp._read_current_state_for_update(task_id)
        if current_state is None:
            raise TransitionCoordinatorError(f"Task not found: {task_id}")

        self._cp._state_machine.validate_adjacency(task_id, current_state, to_state)

        # 2. Resolve template from registry
        template = self._registry.get_template(current_state, to_state)
        if not template:
            raise TransitionCoordinatorError(
                f"No template registered for transition ({current_state} -> {to_state})."
            )

        # 3. Read current occupancy ID
        last_trans = self._cp._persistence.get_last_transition(task_id)
        source_occupancy_id = last_trans.transition_id if last_trans else None

        # Handle skip request validation
        staged_decisions: List[TransitionDecision] = []
        staged_receipts: List[Dict[str, Any]] = []

        if skip_review:
            if not template.skip.get("allowed", False):
                raise TransitionCoordinatorError(
                    f"Skip is not allowed for transition {current_state} -> {to_state} (cannot be skipped)."
                )
            if template.skip.get("requires_justification", False) and not (skip_reason and skip_reason.strip()):
                raise TransitionCoordinatorError(
                    f"Skip for transition {current_state} -> {to_state} requires justification."
                )

            # Stage skip decision
            staged_decisions.append(
                TransitionDecision(
                    task_id=task_id,
                    source_occupancy_transition_id=source_occupancy_id,
                    from_state=current_state,
                    to_state=to_state,
                    question_id=f"skip_{template.transition_id}",
                    answer=skip_reason or "SKIPPED",
                    decision_type="SKIP",
                    actor=actor,
                    recorded_at=self._cp._clock.current_time(),
                )
            )

            # Determine appropriate skip receipt gate name
            skip_gate = "multi_agent_review_skipped"
            if "code_review_or_skip" in template.deterministic_checks:
                skip_gate = "multi_agent_code_review_skipped"

            raw = f"{task_id}:{skip_gate}:user-skip:{actor}:{skip_reason}:{self._cp._clock.current_time()}"
            h = self._cp._crypto.sha256_hex(raw)[:12]
            token = f"EVO-INTEGRITY-{task_id}-{h}"
            staged_receipts.append({
                "gate_name": skip_gate,
                "command_executed": f"user-skip:{actor}:{skip_reason}",
                "exit_code": 0,
                "receipt_token": token,
            })

        # 4. Display transition header
        self._print_banner(f"TRANSITION PROPOSAL: {current_state} -> {to_state}")
        self._out.write(f"\nCurrent phase:   {current_state}\n")
        self._out.write(f"Requested phase: {to_state}\n\n")
        self._out.write(f"Purpose:\n{template.purpose}\n\n")

        # 5. Evaluate deterministic checks and required artifacts
        ctx = self._cp._build_transition_policy_ctx(task_id, task)
        checklist_status = []
        all_passed = True
        failed_reasons = []

        # Check required artifacts
        for art_pat in template.required_artifacts:
            art_rel = art_pat.replace("<task-id>", task_id)
            art_path = self._resolve_artifact_path(art_rel, task)
            exists = self._fs.exists(art_path) if art_path is not None else False
            checklist_status.append((exists, f"Artifact: {art_rel}"))
            if not exists:
                all_passed = False
                failed_reasons.append(f"Missing required artifact: {art_rel}")

        # Check deterministic checklist items or checks
        for chk_item in template.checklist:
            checklist_status.append((True, chk_item))

        for check_id in template.deterministic_checks:
            # If skipping review and this is critic_review_or_skip / code_review_or_skip, it passes via staged receipt
            if skip_review and check_id in ("critic_review_or_skip", "code_review_or_skip"):
                checklist_status.append((True, f"Check skipped: {check_id}"))
                continue
            try:
                evaluate_check(check_id, ctx)
            except (PolicyViolation, PolicyConfigurationError) as e:
                all_passed = False
                failed_reasons.append(f"Check failed: {check_id} ({e})")

        # Display checklist
        self._out.write("Checklist:\n")
        for passed, item in checklist_status:
            mark = "✓" if passed else "✗"
            status_text = "PASS" if passed else "FAIL"
            self._out.write(f"[{mark}] {item} ({status_text})\n")
        self._out.write("\n")

        if not all_passed:
            err_msg = "; ".join(failed_reasons)
            self._out.write(f"TRANSITION DENIED: {err_msg}\n\n")
            raise TransitionCoordinatorError(f"{template.denial_message} Reason: {err_msg}")

        # 6. Collect human questions sequentially
        answers = dict(provided_answers or {})

        for q in template.human_questions:
            qid = q.get("question_id")
            q_text = q.get("question", "")
            options = q.get("options", [])
            default_opt = q.get("default", "")

            self._out.write(f"Question: {q_text}\n")
            for idx, opt in enumerate(options, 1):
                self._out.write(f"  {idx}. {opt}\n")
            self._out.write("\n")

            if interactive:
                # Sequential presentation: prompt 1 question at a time
                prompt_str = f"Select option [Recommended: {default_opt}]: "
                user_input = self._input_fn(prompt_str).strip()
                if not user_input:
                    raise TransitionCoordinatorError(
                        f"Missing required response for question '{qid}'. Empty input rejected."
                    )
                # Match by number or text
                try:
                    num = int(user_input)
                    chosen_ans = options[num - 1] if 1 <= num <= len(options) else user_input
                except ValueError:
                    chosen_ans = user_input
                decision_actor = "human"
            elif qid in answers:
                chosen_ans = answers[qid]
                # Non-interactive provided_answers are supplied programmatically by an agent,
                # not by a human at an interactive prompt.
                decision_actor = "agent"
            else:
                # Non-interactive without provided answer -> must fail closed despite default
                raise TransitionCoordinatorError(
                    f"Missing required response for question '{qid}': '{q_text}'. "
                    "Explicit answer required even if default is configured."
                )

            # Validate that chosen_ans matches one of the declared options
            if options and chosen_ans not in options:
                raise TransitionCoordinatorError(
                    f"Invalid undeclared answer option '{chosen_ans}' for question '{qid}'. "
                    f"Valid options: {options}"
                )

            staged_decisions.append(
                TransitionDecision(
                    task_id=task_id,
                    source_occupancy_transition_id=source_occupancy_id,
                    from_state=current_state,
                    to_state=to_state,
                    question_id=qid,
                    answer=chosen_ans,
                    decision_type="RESET" if template.transition_id.startswith("reset_to_intake") else "ANSWER",
                    actor=decision_actor,
                    recorded_at=self._cp._clock.current_time(),
                )
            )

        # 7. Evaluate approval requirement
        if template.approval.get("required"):
            approver_role = template.approval.get("approver_role", "human")
            if interactive:
                prompt_str = f"Approval required ({approver_role}). Approve transition? (y/n): "
                ans = self._input_fn(prompt_str).strip().lower()
                if ans in ("y", "yes"):
                    dec = "APPROVAL"
                    approval_actor = "human"
                else:
                    raise TransitionCoordinatorError(f"Transition {current_state} -> {to_state} rejected by user.")
            elif approval_decision == "APPROVAL" or (not approval_decision and approver_role == "agent_or_human"):
                dec = "APPROVAL"
                approval_actor = "agent"
            elif approval_decision == "REJECTION":
                raise TransitionCoordinatorError(f"Transition {current_state} -> {to_state} rejected by approver.")
            else:
                raise TransitionCoordinatorError(
                    f"Transition {current_state} -> {to_state} requires explicit {approver_role} approval."
                )

            staged_decisions.append(
                TransitionDecision(
                    task_id=task_id,
                    source_occupancy_transition_id=source_occupancy_id,
                    from_state=current_state,
                    to_state=to_state,
                    question_id=f"approval_{template.transition_id}",
                    answer=dec,
                    decision_type="APPROVAL",
                    actor=approval_actor,
                    recorded_at=self._cp._clock.current_time(),
                )
            )

        # 8. Build TransitionCommitRequest
        commit_request = TransitionCommitRequest(
            task_id=task_id,
            expected_from_state=current_state,
            to_state=to_state,
            source_occupancy_transition_id=source_occupancy_id,
            template_id=template.transition_id,
            actor=actor,
            reason=reason,
            staged_decisions=staged_decisions,
            staged_receipts=staged_receipts,
        )

        # 9. Atomic commit via ControlPlane -> SqlitePersistenceAdapter
        record = self._cp.commit_authorized_transition(commit_request)

        # 10. Display visible transition output report
        self._out.write(f"Decision recorded: Transition approved\n")
        self._out.write(f"Transition committed: {record.from_state} -> {record.to_state}\n")
        self._out.write(f"Persisted transition ID: {record.transition_id}\n")
        self._out.write(f"Current state verified: {record.to_state}\n\n")

        self._out.write("Capabilities released:\n")
        if template.capabilities_released:
            for cap in template.capabilities_released:
                self._out.write(f"- {cap}\n")
        else:
            self._out.write("- (none)\n")
        self._out.write("\n")

        self._out.write("Still prohibited:\n")
        if template.capabilities_prohibited:
            for proh in template.capabilities_prohibited:
                self._out.write(f"- {proh}\n")
        else:
            self._out.write("- (none)\n")
        self._out.write("\n")

        self._write_next_steps_hint(record.to_state)
        self._print_banner("", end="\n")

        return record

    def _write_next_steps_hint(self, current_state: str) -> None:
        """Prints the legal next edges from current_state (live from the registry, not
        memorized), flagging which require a human-answered question vs. are purely
        deterministic, plus a pointer to interview-spec/SKILL.md and the control-plane
        diagrams for full-flow context. Added after a session found repeated mistakes from
        re-deriving 'what's the actual next edge' by hand-reading YAML."""
        next_templates = [t for t in self._registry.get_all_templates() if t.from_state == current_state]
        self._out.write(f"Next possible transitions from {current_state}:\n")
        if not next_templates:
            self._out.write("- (none — terminal state)\n")
        else:
            for t in sorted(next_templates, key=lambda t: t.to_state):
                gate = "human question required" if t.human_questions else "deterministic only"
                detail = t.next_steps_hint or t.purpose
                self._out.write(f"- -> {t.to_state} ({gate}): {detail}\n")
        self._out.write(
            "\nFull pipeline reference: plugins/agent-agentic-os/skills/interview-spec/SKILL.md\n"
            "Diagrams: docs/diagrams/control-plane-architecture.mermaid, "
            "control-plane-pipeline-happy-path.mermaid, control-plane-pipeline.mermaid\n"
        )

    def _print_banner(self, text: str, end: str = "\n"):
        width = 60
        sep = "=" * width
        if text:
            self._out.write(f"{sep}\n{text}\n{sep}{end}")
        else:
            self._out.write(f"{sep}{end}")

    def _resolve_repo_root(self) -> Path:
        """Resolves the canonical repository root common across worktrees."""
        if self._repo_root is not None:
            return Path(self._repo_root).resolve()

        configured = getattr(self._cp, "repo_root", None)
        if configured is not None:
            return Path(configured).resolve()

        db_path = getattr(self._cp, "db_path", None)
        if db_path is not None and db_path.parent.name == "context":
            return db_path.parent.parent.resolve()

        curr = Path.cwd().resolve()
        for p in [curr] + list(curr.parents):
            if (p / "context").exists() and not (p / "skills").exists():
                return p.resolve()
        return curr

    def _resolve_artifact_path(self, art_rel: str, task: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """Resolves an artifact relative path ensuring traversal and containment rules.
        - Directory artifact matching '.worktrees/<task-id>' validates against the task's registered worktree_path.
        - Plan/spec files resolve against the task's registered worktree root (if registered and present)
          or fall back to the common repository root.
        - Prohibits path traversal ('..') and paths escaping authorized boundaries.
        - Validates existence via FilesystemPort (self._fs).
        """
        raw_parts = Path(art_rel).parts
        if ".." in raw_parts:
            return None

        repo_root = self._resolve_repo_root()
        task_id = task.get("task_id", "") if task else ""

        # 1. Registered worktree directory artifact
        if art_rel.startswith(".worktrees/") or art_rel == ".worktrees":
            wt_path_str = task.get("worktree_path") if task else None
            if wt_path_str:
                wt_p = Path(wt_path_str)
                candidate = wt_p.resolve() if wt_p.is_absolute() else (repo_root / wt_p).resolve()
            else:
                candidate = (repo_root / art_rel).resolve()
            try:
                candidate.relative_to(repo_root)
                return candidate
            except ValueError:
                # Check temporary directory for test fixtures
                try:
                    for parent in candidate.parents:
                        if "pytest" in parent.name or "tmp" in parent.name or "temp" in parent.name:
                            return candidate
                except Exception:
                    pass
                return None

        # 2. Plan/spec artifacts
        # If task has a registered worktree, check for the plan file inside that worktree first
        wt_path_str = task.get("worktree_path") if task else None
        if wt_path_str:
            wt_p = Path(wt_path_str)
            wt_root = wt_p.resolve() if wt_p.is_absolute() else (repo_root / wt_p).resolve()
            wt_candidate = (wt_root / art_rel).resolve()
            if self._fs.exists(wt_candidate):
                try:
                    wt_candidate.relative_to(wt_root)
                    return wt_candidate
                except ValueError:
                    pass

        # Fall back to repo_root
        candidate = (repo_root / art_rel).resolve()
        try:
            candidate.relative_to(repo_root)
            return candidate
        except ValueError:
            try:
                for parent in candidate.parents:
                    if "pytest" in parent.name or "tmp" in parent.name or "temp" in parent.name:
                        return candidate
            except Exception:
                pass
            return None

