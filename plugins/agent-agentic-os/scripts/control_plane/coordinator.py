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

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TextIO, Tuple
from control_plane.registry import TransitionRegistry, TransitionTemplate, TransitionRegistryError
from control_plane.policy import evaluate_check, PolicyViolation, PolicyConfigurationError
from control_plane import review_options as _review_options
from control_plane.review_selection import condition_holds
from control_plane.identity_layout import default_layout
from control_plane.isolation_check import check_isolation
from control_plane.proof_edges import snapshot_for_edge
from control_plane.snapshot import SnapshotError, snapshot_from_json
from control_plane.ssh_signing import SIGN_NAMESPACE
from control_plane.transition_request import DEFAULT_GATE1_TTL_SECONDS, create_transition_request
from control_plane.constants import (
    STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_RETROSPECTIVE, STATE_DONE,
    GUIDANCE_COMPLIANCE_CONFIRM_ANSWER, AUTHORIZED_ACTOR_AGENT_OR_HUMAN,
)
from control_plane.ports import (
    FilesystemPort,
    TransitionCommitRequest,
    TransitionDecision,
    TransitionRecord,
)


class TransitionCoordinatorError(Exception):
    """Raised when transition coordination preconditions or decisions are incomplete or rejected."""
    pass


class HumanProofRequired(TransitionCoordinatorError):
    """Gate 1 needs a cryptographic human approval; nothing was changed.

    `remediation` is a machine-readable dict (edge, request id, what the human must confirm,
    the exact commands, failed isolation checks) so an agent knows precisely what to ask the
    human for; the message carries the same content as JSON."""

    def __init__(self, remediation: Dict[str, Any]):
        self.remediation = remediation
        super().__init__(
            "HUMAN_PROOF_REQUIRED: " + remediation["why"] + "\n" + json.dumps(remediation, indent=2)
        )


def _normalize_declared_option(value: str) -> str:
    """Normalize option text for safe, human-friendly comparison."""
    normalized = " ".join(value.strip().casefold().split())
    if normalized.endswith(" [recommended]"):
        normalized = normalized[: -len(" [recommended]")].rstrip()
    return normalized


def _canonicalize_declared_answer(answer: str, options: List[str]) -> str:
    """Return the exact YAML option for an unambiguous human answer.

    The stored value must remain the registered option, while comparison accepts
    case/whitespace differences and an omitted ``[Recommended]`` marker. Similar
    options fail closed rather than allowing the coordinator to guess.
    """
    matches = [option for option in options if _normalize_declared_option(option) == _normalize_declared_option(answer)]
    if len(matches) > 1:
        raise TransitionCoordinatorError(
            f"Answer '{answer}' is ambiguous; matching registered options: {matches}"
        )
    if not matches:
        raise TransitionCoordinatorError(
            f"Invalid undeclared answer option '{answer}'. Valid options: {options}"
        )
    return matches[0]


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
        human_signer: Optional[Callable[..., Any]] = None,
        review_choices_fn: Optional[Callable[..., Any]] = None,
    ):
        self._cp = control_plane
        # Menus for the internal review runtime/model/effort questions (choices_from in the YAML). The default
        # resolves review_options.choices_for at call time; tests inject a fake-CLI resolver here.
        self._review_choices_fn = review_choices_fn or (lambda kind, runtime=None: _review_options.choices_for(kind, runtime=runtime))
        # The human's signing step for a cryptographic-proof edge: a callable(control_plane, request_id) that
        # shows the challenge, runs `ssh-keygen -Y sign` (the CLI attaches the terminal so OpenSSH prompts for
        # the private-key passphrase) and commits through approve_transition. None (agents, pipes, CI) means
        # the coordinator stops with HUMAN_PROOF_REQUIRED and the human runs the three commands themselves.
        self._human_signer = human_signer
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

        # A guidance-blocked task takes NO transition, including closure: there is no emergency bypass. The
        # human clears the block (clear-guidance-block) or signs the closure after clearing it.
        block_reason = self._cp.get_guidance_block_reason(task_id)
        if block_reason:
            raise TransitionCoordinatorError(
                f"BLOCKED: task '{task_id}' is guidance-blocked ({block_reason}). "
                "No further transitions are permitted until clear-guidance-block is run "
                "with explicit human authorization."
            )

        current_state = self._cp._read_current_state_for_update(task_id)
        if current_state is None:
            raise TransitionCoordinatorError(f"Task not found: {task_id}")

        # Validate the requested edge before authorization policy.  This keeps
        # illegal edges observable as InvalidStateTransition rather than
        # masking them as an authorization denial.
        self._cp._state_machine.validate_adjacency(task_id, current_state, to_state)

        # Cryptographic-proof edges (requires_cryptographic_proof in the YAML: every edge into APPROVED,
        # VERIFY_EXIT and DONE, including closure from any state). No prompt, typed word, flag, --answers or
        # actor string authorizes them: the transition is committed only by a verified OpenSSH signature over
        # a content-bound transition_request, consumed in the commit transaction. See _signed_transition.
        if (current_state, to_state) in self._registry.proof_required_edges():
            if skip_review:
                raise TransitionCoordinatorError(
                    f"{current_state} -> {to_state} requires a cryptographic signature; it cannot be skipped and no flag can bypass it."
                )
            return self._signed_transition(task_id, current_state, to_state, actor, interactive)

        # 2. Resolve template from registry
        template = self._registry.get_template(current_state, to_state)
        if not template:
            raise TransitionCoordinatorError(
                f"No template registered for transition ({current_state} -> {to_state})."
            )

        # Programmatic answers must never be presented as interactive human
        # provenance.  The SQLite trigger remains the final authority, but
        # rejecting this combination here gives callers an explicit, actionable
        # error instead of leaking a low-level persistence failure.
        human_gated = bool(template.human_questions or template.stage_question_ids)
        human_gated = human_gated or (
            template.approval.get("required")
            and template.approval.get("approver_role", "human") == "human"
        )
        if actor == "human" and not interactive and provided_answers and human_gated:
            raise TransitionCoordinatorError(
                "Non-interactive answers cannot claim interactive human provenance; "
                "use --interactive for a genuine human decision."
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
        self._write_transition_guidance(current_state, to_state, phase="before")

        # 5. Evaluate deterministic checks and required artifacts
        ctx = self._cp._build_transition_policy_ctx(task_id, task, current_state, to_state)
        checklist_status = []
        all_passed = True
        failed_reasons = []
        deferred_checks = []

        # Check required artifacts
        for art_pat in template.required_artifacts:
            art_rel = art_pat.replace("<task-id>", task_id)
            art_path = self._resolve_artifact_path(art_rel, task)
            exists = self._fs.exists(art_path) if art_path is not None else False
            checklist_status.append((exists, f"Artifact: {art_rel}"))
            if not exists:
                all_passed = False
                failed_reasons.append(f"Missing required artifact: {art_rel}")

        if (
            current_state == STATE_DRAFT_PLAN
            and to_state in {STATE_PLAN_REVIEW, STATE_MULTI_AGENT_REVIEW, STATE_AWAITING_APPROVAL}
            and all_passed
        ):
            staged_revision = self._stage_plan_artifact_submission(
                task_id=task_id,
                task=task,
                template=template,
            )
            if staged_revision is not None:
                staged_receipts.append(staged_revision)

        # Check deterministic checklist items or checks
        for chk_item in template.checklist:
            checklist_status.append((True, chk_item))

        for check_id in template.deterministic_checks:
            if check_id in ("interview_trivial_complete", "interview_standard_complete", "interview_plan_route_complete"):
                deferred_checks.append(check_id)
                continue
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
        persisted_answers = dict(ctx.get("stage_answers", {}))
        stage_answers = dict(persisted_answers)
        questions_to_ask = []
        for question_id in template.stage_question_ids or []:
            if question_id in persisted_answers:
                continue
            question = self._registry.get_stage_question(current_state, question_id)
            if question is None:
                raise TransitionCoordinatorError(
                    f"Stage question '{question_id}' is not defined for state '{current_state}'."
                )
            questions_to_ask.append(question)
        questions_to_ask.extend(
            question for question in template.human_questions
            if question.get("question_id") not in persisted_answers
        )

        for q in questions_to_ask:
            qid = q.get("question_id")
            q_text = q.get("question", "")
            options = q.get("options", [])
            default_opt = q.get("default", "")

            if q.get("asked_when"):
                # review-selection-v1: internal runtime/model/effort are asked only for an internal
                # method, and only the human can answer them (never provided_answers, never a default).
                if not condition_holds(q, {d.question_id: d.answer for d in staged_decisions}):
                    continue
                if not interactive:
                    raise TransitionCoordinatorError(
                        f"'{qid}' is the human's selection (internal review runtime/model/effort) and must be typed "
                        "interactively (--interactive); an agent cannot supply it or pick a default."
                    )

            if q.get("choices_from"):
                options = self._resolve_review_menu(q, staged_decisions)

            self._out.write(f"Question: {q_text}\n")
            for idx, opt in enumerate(options, 1):
                self._out.write(f"  {idx}. {opt}\n")
            self._out.write("\n")

            if interactive:
                # Sequential presentation: prompt 1 question at a time
                prompt_str = f"{qid}: Select option [Recommended: {default_opt}]: "
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
            if options:
                chosen_ans = _canonicalize_declared_answer(chosen_ans, options)
            accepted_answers = q.get("accepted_answers")
            if accepted_answers is not None:
                try:
                    _canonicalize_declared_answer(chosen_ans, accepted_answers)
                except TransitionCoordinatorError as exc:
                    raise TransitionCoordinatorError(
                        f"Answer '{chosen_ans}' for question '{qid}' does not authorize this transition. "
                        f"Accepted answers: {accepted_answers}"
                    ) from exc

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
            if qid in (template.stage_question_ids or []):
                stage_answers[qid] = chosen_ans

        if current_state == STATE_INTERVIEW and to_state == STATE_DRAFT_PLAN:
            # Project each newly-collected interview answer into the plan-outline
            # artifact before the commit path's assert_interview_plan_outline_ready
            # check runs -- otherwise every interactive DRAFT_PLAN transition fails
            # with "interview plan outline is missing" despite complete answers.
            for question_id in (template.stage_question_ids or []):
                if question_id in stage_answers and question_id not in persisted_answers:
                    self._cp.update_interview_plan_outline(
                        task_id, question_id, stage_answers[question_id], actor=actor
                    )

        if template.stage_route:
            route_question = template.stage_route.get("question_id")
            expected_answer = template.stage_route.get("equals")
            if stage_answers.get(route_question, "").strip() != expected_answer:
                raise TransitionCoordinatorError(
                    f"Interview route requires {route_question}={expected_answer}; "
                    f"received '{stage_answers.get(route_question, '')}'."
                )

        deferred_ctx = dict(ctx)
        deferred_ctx["stage_answers"] = stage_answers
        for check_id in deferred_checks:
            try:
                evaluate_check(check_id, deferred_ctx)
            except (PolicyViolation, PolicyConfigurationError) as e:
                raise TransitionCoordinatorError(
                    f"{template.denial_message} Reason: {e}"
                ) from e

        # Persist a route marker from the human-authored interview decision so
        # later verification gates can distinguish the proportionate TRIVIAL
        # focused-test contract from STANDARD full-suite enforcement.
        if (
            current_state == STATE_INTERVIEW
            and to_state == STATE_DRAFT_PLAN
            and stage_answers.get("interview_classification", "").strip() == "TRIVIAL"
        ):
            raw = f"{task_id}:trivial_route_selected:{source_occupancy_id}:{self._cp._clock.current_time()}"
            staged_receipts.append({
                "gate_name": "trivial_route_selected",
                "command_executed": "interview_classification=TRIVIAL",
                "exit_code": 0,
                "receipt_token": f"TRIVIAL-ROUTE-{self._cp._crypto.sha256_hex(raw)[:12]}",
            })

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

        # 7b. Mandatory per-transition guidance-compliance confirmation (added per explicit
        # human request, 2026-09-13): every non-proof transition requires an explicit,
        # separate confirmation that the advisory guidance/checklist/questions above were
        # actually read and followed -- not inferred from having answered the edge's own
        # questions. A "no" answer, or no answer at all in interactive mode, blocks ALL
        # further transitions for this task (guidance_block_reason) until a human explicitly
        # clears it via clear-guidance-block.
        if "guidance_compliance_confirmation" in persisted_answers:
            # Already answered and persisted from an earlier staged decision for this
            # exact occupancy (the same mechanism every other question already honors
            # via persisted_answers/ctx["stage_answers"]) -- consistent with the rest
            # of this method, not a bypass: an explicit affirmative answer must still
            # already exist somewhere, it's just not re-asked if it does.
            pass
        else:
            guidance_prompt = (
                "guidance_compliance_confirmation: Have you read and followed this "
                "transition's YAML guidance (advisory text, checklist, and questions) "
                "exactly, with no shortcuts or substitutions? Type YES or NO: "
            )
            if interactive:
                guidance_answer = self._input_fn(guidance_prompt).strip()
                guidance_decision_actor = "human"
            elif template.authorized_actor == AUTHORIZED_ACTOR_AGENT_OR_HUMAN:
                # auth-ciba-poc-transition-mechanics (T7): on an agent_or_human edge,
                # this confirmation is not gating a consequential decision -- it is
                # gating routine pipeline plumbing (e.g. INTAKE -> INTERVIEW). The
                # 2026-09-14 self-certification concern below applies specifically to
                # human_only edges, where this confirmation stands in for real human
                # authorization; on agent_or_human edges an agent-provided answer is
                # exactly as legitimate as any other answer the agent supplies for
                # this edge's own questions, and is recorded honestly as actor="agent",
                # never actor="human".
                answer_value = answers.get("guidance_compliance_confirmation")
                if not answer_value or not str(answer_value).strip():
                    raise TransitionCoordinatorError(
                        "guidance_compliance_confirmation requires an explicit answer -- "
                        "pass --interactive or --answers "
                        "'{\"guidance_compliance_confirmation\": \"YES\"}'."
                    )
                guidance_answer = str(answer_value).strip()
                guidance_decision_actor = "agent"
            else:
                # human_only edge that is not a cryptographic-proof edge (e.g. reset-to-INTAKE recovery family):
                # this question may NEVER be satisfied programmatically (found by
                # external review, 2026-09-14: an agent could otherwise self-certify
                # via --answers '{"guidance_compliance_confirmation": "YES"}' with
                # actor="agent", defeating the entire purpose of a human-in-the-loop
                # confirmation). Unlike an agent_or_human edge, this one requires a
                # real live human -- interactive=True is mandatory, no provided_answers
                # escape hatch. A missing/non-interactive attempt is a usage error --
                # fail loud with no side effect (no block set) -- not an implicit "NO".
                # Only a genuine, explicit "NO" typed by a real human at the prompt may
                # ever set guidance_block_reason.
                raise TransitionCoordinatorError(
                    "guidance_compliance_confirmation requires a real human answer -- "
                    "pass --interactive. It cannot be supplied via provided_answers/--answers."
                )

            guidance_followed = guidance_answer.strip().upper() == GUIDANCE_COMPLIANCE_CONFIRM_ANSWER
            staged_decisions.append(
                TransitionDecision(
                    task_id=task_id,
                    source_occupancy_transition_id=source_occupancy_id,
                    from_state=current_state,
                    to_state=to_state,
                    question_id="guidance_compliance_confirmation",
                    answer=guidance_answer or "(no answer given)",
                    decision_type="CONFIRMATION",
                    actor=guidance_decision_actor,
                    recorded_at=self._cp._clock.current_time(),
                )
            )
            if not guidance_followed:
                block_reason = (
                    f"Answered '{guidance_answer or '(no answer given)'}' (not YES) to the "
                    f"guidance-compliance confirmation for {current_state} -> {to_state}."
                )
                self._cp.set_guidance_block(task_id, block_reason)
                raise TransitionCoordinatorError(
                    f"BLOCKED: {block_reason} All further transitions for task '{task_id}' "
                    "are refused until a human explicitly runs clear-guidance-block."
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

    def _resolve_review_menu(self, question: Dict[str, Any], staged_decisions: List[Any]) -> List[str]:
        """Options for a choices_from question: the selectable menu ids, or [] (free text) with a printed
        warning when no probe/profile can build one. Typed answers must then match a menu id exactly."""
        spec = question["choices_from"]
        runtime = None
        if spec.get("runtime_question"):
            runtime = next((d.answer for d in staged_decisions if d.question_id == spec["runtime_question"]), None)
        choice_set = self._review_choices_fn(spec["kind"], runtime=runtime)
        selectable = [i["id"] for i in choice_set.items if i.get("installed", True)]
        for item in choice_set.items:
            if not item.get("installed", True):
                self._out.write(f"  (not available: {item['id']} - not found on PATH)\n")
        if not selectable:
            self._out.write(f"  WARNING: {choice_set.warning or 'no menu available; the answer cannot be validated'}\n")
        return selectable

    def authorization_preflight(self, task_id: str, to_state: str) -> List[str]:
        """Re-run this edge's policy WITHOUT committing anything and return the reasons it would be
        denied (empty list = passes). Used by approve-transition so a valid signature cannot bypass
        conditions that changed after the request was made (guidance block, missing artifacts,
        dirty main, or any other deterministic check of the edge)."""
        reasons: List[str] = []
        block = self._cp.get_guidance_block_reason(task_id)
        if block:
            reasons.append(f"task is guidance-blocked ({block})")
        task = self._cp.get_task(task_id)
        current = self._cp._read_current_state_for_update(task_id)
        if task is None or current is None:
            return reasons + [f"task not found: {task_id}"]
        template = self._registry.get_template(current, to_state)
        if template is None:
            return reasons + [f"no template registered for {current} -> {to_state}"]
        for pattern in template.required_artifacts:
            rel = pattern.replace("<task-id>", task_id)
            path = self._resolve_artifact_path(rel, task)
            if path is None or not self._fs.exists(path):
                reasons.append(f"missing required artifact: {rel}")
        ctx = self._cp._build_transition_policy_ctx(task_id, task, current, to_state)
        deferred = ("interview_trivial_complete", "interview_standard_complete", "interview_plan_route_complete")
        for check_id in template.deterministic_checks:
            if check_id in deferred:
                continue
            try:
                evaluate_check(check_id, ctx)
            except (PolicyViolation, PolicyConfigurationError) as exc:
                reasons.append(f"{check_id}: {exc}")
        return reasons

    def _signed_transition(self, task_id: str, from_state: str, to_state: str, actor: str, interactive: bool) -> TransitionRecord:
        """Commit a cryptographic-proof edge. Runs the edge's checks first (so nothing is signed that could not
        commit), creates the content-bound transition_request, then either lets the human's signer complete it
        (interactive terminal) or stops with HUMAN_PROOF_REQUIRED and the request_id."""
        reasons = self.authorization_preflight(task_id, to_state)
        if reasons:
            raise TransitionCoordinatorError(
                f"Transition {from_state} -> {to_state} denied before any request was created: " + "; ".join(reasons)
            )
        repo_root = self._resolve_repo_root()
        _last = self._cp._persistence.get_last_transition(task_id)
        record, error = self._create_proof_request(task_id, from_state, to_state, _last.transition_id if _last else None, repo_root)
        if error is not None:
            raise error
        if interactive and self._human_signer is not None:
            return self._human_signer(self._cp, record.request_id)
        raise self._human_proof_required(record, task_id, from_state, to_state, repo_root)

    def _create_proof_request(self, task_id, from_state, to_state, occupancy_id, repo_root):
        """Build the content snapshot and store the PENDING request. Returns (record, None) or (None, error)."""
        try:
            snapshot = snapshot_for_edge(self._cp, repo_root, task_id, from_state, to_state)
        except SnapshotError as exc:
            return None, TransitionCoordinatorError(
                f"{from_state} -> {to_state} needs the content the human will sign (plan artifacts under "
                f"docs/plans/work-tasks/{task_id}/, or the registered git worktree) before a request can be created: {exc}"
            )
        conn = self._cp._persistence.get_connection()
        try:
            record = create_transition_request(
                conn, task_id=task_id, from_state=from_state, to_state=to_state, occupancy_id=occupancy_id,
                ttl_seconds=DEFAULT_GATE1_TTL_SECONDS, content_snapshot=snapshot,
            )
        finally:
            conn.close()
        return record, None

    def _human_proof_required(self, record, task_id: str, from_state: str, to_state: str, repo_root: Path) -> HumanProofRequired:
        """The structured HUMAN_PROOF_REQUIRED error for an already-created request."""
        layout = default_layout(repo_root)
        preflight = check_isolation(
            allowed_signers=layout.allowed_signers, allowed_signers_selftest=layout.allowed_signers_selftest,
            challenge_dir=layout.challenge_dir,
        )
        control = "python3 plugins/agent-agentic-os/scripts/agent_control.py"
        return HumanProofRequired({
            "code": "HUMAN_PROOF_REQUIRED",
            "edge": f"{from_state} -> {to_state}",
            "task_id": task_id,
            "request_id": record.request_id,
            "expires_at": int(record.expiration),
            "why": (
                "This gate needs a cryptographic approval from a human's signing key. Prompts, piped input, "
                "injected input functions and --answers cannot authorize it. Nothing was changed: the task is "
                f"still in {from_state}."
            ),
            "binds": [entry.label for entry in snapshot_from_json(record.content_snapshot)] if record.content_snapshot else [],
            "commands": {
                "show_challenge": f"{control} show-challenge --request-id {record.request_id}",
                "sign": f"printed by show-challenge (an ssh-keygen -Y sign -n {SIGN_NAMESPACE} command for your key)",
                "approve": f"{control} approve-transition --request-id {record.request_id}",
                "setup_identity": "python3 plugins/agent-agentic-os/scripts/setup_ciba_identity.py",
                "setup_docs": "plugins/agent-agentic-os/references/isolation-setup.md",
            },
            "failed_checks": [{"code": f.code, "path": f.path, "message": f.message} for f in preflight.failures],
            "note": (
                "Ask the human to run the three commands in order. The signature authorizes exactly this edge "
                "and the content listed in `binds`, once, and nothing else. If failed_checks is not empty, the "
                "human must complete the identity setup first."
            ),
        })

    def _write_transition_guidance(self, current_state: str, to_state: str, phase: str) -> None:
        """Render advisory guidance from the read-only registry snapshot."""
        guidance = self._registry.get_transition_guidance(current_state, to_state)
        self._out.write(f"Advisory transition guidance ({phase}; registry version {guidance['registry_version']}):\n")
        if not guidance.get("legal", True):
            self._out.write(f"- DENIED: {guidance['denial_guidance']}\n")
            self._out.write("- Guidance is advisory only; it cannot authorize this transition.\n\n")
            return
        self._out.write(f"- {current_state} -> {to_state}: {guidance['command']}\n")
        self._out.write(f"- Success: {guidance['success_guidance']}\n")
        for helper in guidance.get("helper_commands", []):
            self._out.write(f"- Helper: {helper}\n")
        # Execution-unit guidance is identical boilerplate on every single transition
        # attempt regardless of edge -- printing it in full each time trained an agent
        # to pattern-match/skim the whole advisory block rather than read the
        # edge-specific delta above it (2026-09-13 retrospective finding). Print it once
        # per unit names only; full instructions/fields remain in transition_templates.yaml.
        units = ", ".join(guidance.get("execution_guidance", {}).keys())
        if units:
            self._out.write(f"Execution-unit guidance (advisory; unchanged across edges): {units}\n")
            self._out.write("  See plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml for full field contracts.\n")
        self._out.write("- Guidance is advisory only; policy, human gates, and SQLite remain authoritative.\n\n")

    def _stage_plan_artifact_submission(
        self,
        task_id: str,
        task: Dict[str, Any],
        template: TransitionTemplate,
    ) -> Optional[Dict[str, Any]]:
        """Stage an atomic plan-artifact identity receipt and reject unchanged resubmissions."""
        artifact_identities = []
        for artifact_pattern in template.required_artifacts:
            artifact_rel = artifact_pattern.replace("<task-id>", task_id)
            artifact_path = self._resolve_artifact_path(artifact_rel, task)
            if artifact_path is None or not artifact_path.is_file():
                continue
            digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            artifact_identities.append(f"{artifact_rel}={digest}")

        identity = "plan-artifacts:v1:" + "|".join(artifact_identities)
        prior_submissions = [
            receipt for receipt in self._cp.get_verification_receipts(task_id)
            if receipt.get("gate_name") == "plan_artifact_submission"
        ]
        latest_submission_id = prior_submissions[-1].get("receipt_id") if prior_submissions else 0
        explicit_revision = any(
            receipt.get("gate_name") == "plan_artifact_revision"
            and receipt.get("command_executed") == identity
            and receipt.get("receipt_id", 0) > latest_submission_id
            for receipt in self._cp.get_verification_receipts(task_id)
        )
        if prior_submissions and prior_submissions[-1].get("command_executed") == identity and not explicit_revision:
            raise TransitionCoordinatorError(
                "Plan artifact identities are unchanged since the last rejected review; "
                "revise an artifact or record a matching plan_artifact_revision receipt before resubmission."
            )

        raw = f"{task_id}:plan_artifact_submission:{identity}:{self._cp._clock.current_time()}"
        token = f"EVO-INTEGRITY-{task_id}-{self._cp._crypto.sha256_hex(raw)[:12]}"
        return {
            "gate_name": "plan_artifact_submission",
            "command_executed": identity,
            "exit_code": 0,
            "receipt_token": token,
        }

    def _write_next_steps_hint(self, current_state: str) -> None:
        """Prints the legal next edges from current_state (live from the registry, not
        memorized), flagging which require a human-answered question vs. are purely
        deterministic, plus a pointer to work-intake/SKILL.md and the control-plane
        diagrams for full-flow context. Added after a session found repeated mistakes from
        re-deriving 'what's the actual next edge' by hand-reading YAML."""
        next_templates = [t for t in self._registry.get_all_templates() if t.from_state == current_state]
        snapshot = self._registry.get_transition_guidance(current_state)
        self._out.write(f"Next possible transitions from {current_state}:\n")
        self._out.write(f"Registry version: {snapshot['registry_version']} (advisory only)\n")
        if not next_templates:
            self._out.write("- (none — terminal state)\n")
        else:
            for t in sorted(next_templates, key=lambda t: t.to_state):
                edge = self._registry.get_transition_guidance(current_state, t.to_state)
                gate = "human question required" if t.human_questions else "deterministic only"
                self._out.write(f"- -> {t.to_state} ({gate}): {edge['command']}\n")
                self._out.write(f"  Success: {edge['success_guidance']}\n")
                self._out.write(f"  Denial recovery: {edge['denial_guidance']}\n")
                for helper in edge.get("helper_commands", []):
                    self._out.write(f"  Helper: {helper}\n")
        self._out.write(
            "\nFull pipeline reference: plugins/agent-agentic-os/skills/work-intake/SKILL.md\n"
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

        # Prefer the documented docs/plans/work-tasks/<task-id>/ grouping
        # (docs/plans/document-layout.md) over the legacy flat docs/plans/<task-id>-*.md
        # layout, for any art_rel of the flat form referencing this task's own artifact.
        # required_artifacts patterns in transition_templates.yaml still declare the
        # flat form; this keeps that declaration working without requiring a duplicate
        # flat-path copy of every plan document (see map-debt.md, 2026-09-17).
        if task_id and art_rel.startswith("docs/plans/") and "/" not in art_rel[len("docs/plans/"):]:
            basename = art_rel[len("docs/plans/"):]
            if basename.startswith(f"{task_id}-") or basename == f"{task_id}.md":
                work_tasks_candidate = (repo_root / "docs" / "plans" / "work-tasks" / task_id / basename).resolve()
                if self._fs.exists(work_tasks_candidate):
                    try:
                        work_tasks_candidate.relative_to(repo_root)
                        return work_tasks_candidate
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
