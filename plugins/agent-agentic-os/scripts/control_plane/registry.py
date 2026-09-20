"""
control_plane/registry.py — TransitionRegistry Domain Component (issue-529 Slice 1)
=====================================================================================

Purpose:
    Loads, schema-validates, and serves the single authoritative transition registry
    (), enforcing 1:1 bidirectional parity with
    state_machine.ALLOWED_TRANSITIONS (edge count derived from that table at
    runtime, not a fixed literal — see test_registry_covers_every_allowed_edge).

Layer:
    OS Kernel / Execution Control Plane Substrate — Registry (domain layer)

Key Input Dependencies:
    - control_plane/transition_templates.yaml (the single authoritative registry
      loaded by load_default()/load_from_file()) — each entry's field set is
      validated against REQUIRED_TEMPLATE_FIELDS.
    - control_plane/state_machine.py's ALLOWED_TRANSITIONS/CANONICAL_STATES — every
      loaded template must have exactly one matching (from_state, to_state) edge.

Key Functions:
    - TransitionRegistryError — raised on a missing/malformed/schema-violating YAML.
    - REQUIRED_TEMPLATE_FIELDS — the field set every template entry must declare.
    - TransitionTemplate — dataclass for one validated transition's full template.
    - TransitionRegistry — loads and serves the registry:
        - get_template()/get_template_by_id() — look up one template.
        - get_all_templates()/get_all_edges()/get_all_declared_check_ids() —
          registry-wide views.
        - get_edges_releasing_capability()/get_legal_next_states() — capability and
          adjacency queries.
        - get_transition_guidance() — builds the human-readable advisory guidance
          block for one edge (purpose, checklist, next steps).
        - get_stage_contract()/get_stage_question() — per-state question contracts.
        - load_from_file()/load_default() — construct a validated registry from a
          given YAML path, or the canonical transition_templates.yaml.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

from control_plane.state_machine import ALLOWED_TRANSITIONS, CANONICAL_STATES
from control_plane.constants import AUTHORIZED_ACTOR_HUMAN_ONLY, AUTHORIZED_ACTOR_AGENT_OR_HUMAN

# load_default() memo: {sha256 of the YAML bytes: parsed registry}; see TransitionRegistry.load_default().
_DEFAULT_REGISTRY_CACHE: Dict[str, "TransitionRegistry"] = {}


class TransitionRegistryError(Exception):
    """Raised when transition_templates.yaml is missing, malformed, or violates schema."""
    pass


REQUIRED_TEMPLATE_FIELDS = [
    "transition_id",
    "from_state",
    "to_state",
    "purpose",
    "checklist",
    "required_artifacts",
    "deterministic_checks",
    "human_questions",
    "approval",
    "skip",
    "authority",
    "capabilities_released",
    "capabilities_prohibited",
    "denial_message",
    "next_steps_hint",
]

TRANSITION_GUIDANCE_SCHEMA_VERSION = "transition-guidance-v1"
EXECUTION_GUIDANCE_UNITS = (
    "work_package",
    "task",
    "slice",
    "transition",
    "execution_step",
)
EXECUTION_GUIDANCE_FIELDS = (
    "objective",
    "scope_boundary",
    "prerequisites",
    "authority",
    "expected_artifacts",
    "validation_command",
    "completion_evidence",
    "handoff_condition",
    "failure_recovery",
)


@dataclass(frozen=True)
class TransitionTemplate:
    transition_id: str
    from_state: str
    to_state: str
    purpose: str
    checklist: List[str]
    required_artifacts: List[str]
    deterministic_checks: List[str]
    human_questions: List[Dict[str, Any]]
    approval: Dict[str, Any]
    skip: Dict[str, Any]
    authority: Dict[str, Any]
    capabilities_released: List[str]
    capabilities_prohibited: List[str]
    denial_message: str
    next_steps_hint: str = ""
    failure_recovery: str = ""
    stage_question_ids: List[str] = None
    stage_route: Optional[Dict[str, Any]] = None
    guidance: Optional[Dict[str, Any]] = None
    # True on every edge into APPROVED, VERIFY_EXIT and DONE: only a verified OpenSSH signature over a
    # content-bound transition_request (consumed in the commit transaction) may commit it.
    requires_cryptographic_proof: bool = False

    @property
    def authorized_actor(self) -> str:
        """Derived, not a hand-maintained parallel field (round-1 review finding,
        auth-ciba-poc-transition-mechanics): 'human_only' iff this edge's own
        approval block requires human approval, otherwise 'agent_or_human'.
        An edge declaring requires_cryptographic_proof is always 'human_only'
        (checked first below): closure edges into DONE take a human signature,
        not a FORCE_CLOSE/FORCE_DONE literal, so they no longer derive as
        'agent_or_human' (changed 2026-09-20)."""
        if self.requires_cryptographic_proof:
            return AUTHORIZED_ACTOR_HUMAN_ONLY
        return (
            AUTHORIZED_ACTOR_HUMAN_ONLY
            if self.approval.get("required") and self.approval.get("approver_role", "human") == "human"
            else AUTHORIZED_ACTOR_AGENT_OR_HUMAN
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "purpose": self.purpose,
            "checklist": list(self.checklist),
            "required_artifacts": list(self.required_artifacts),
            "deterministic_checks": list(self.deterministic_checks),
            "human_questions": list(self.human_questions),
            "approval": dict(self.approval),
            "skip": dict(self.skip),
            "authority": dict(self.authority),
            "capabilities_released": list(self.capabilities_released),
            "capabilities_prohibited": list(self.capabilities_prohibited),
            "denial_message": self.denial_message,
            "next_steps_hint": self.next_steps_hint,
            "failure_recovery": self.failure_recovery,
            "stage_question_ids": list(self.stage_question_ids or []),
            "stage_route": dict(self.stage_route or {}),
            "guidance": dict(self.guidance or {}),
        }


EXECUTION_CLASS_AGENT = "AGENT"
EXECUTION_CLASS_SOFT = "SOFT"
EXECUTION_CLASS_HARD = "HARD"

EXECUTION_CLASS_INSTRUCTIONS = {
    EXECUTION_CLASS_AGENT: "You (the agent) run this once the human has said go in chat. Put their words in --human-confirmed. There is no question to ask.",
    EXECUTION_CLASS_SOFT: "Ask the human in chat, then you run this. Do not hand the command to the human.",
    EXECUTION_CLASS_HARD: "Only the human can run this. Give them the complete command; you cannot run it.",
}


def classify_edge(template: TransitionTemplate) -> Tuple[str, str, str]:
    """Return (run_by, basis, why) for one registry template.

    Rules, in order: signed edge -> HARD/crypto; human_only -> HARD/policy;
    has human questions -> SOFT; otherwise AGENT.
    """
    if template.requires_cryptographic_proof:
        return EXECUTION_CLASS_HARD, "crypto", "Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it."
    if template.authorized_actor == AUTHORIZED_ACTOR_HUMAN_ONLY:
        return EXECUTION_CLASS_HARD, "policy", "Repo policy reserves this human-typed decision to the human."
    if template.human_questions:
        return EXECUTION_CLASS_SOFT, "none", "Has a human question: the human answers in chat, then the agent runs the edge."
    return EXECUTION_CLASS_AGENT, "none", "Deterministic checks only; no human decision is needed."


class TransitionRegistry:
    """Authoritative registry for all transition templates loaded from YAML."""

    def __init__(
        self,
        templates: List[TransitionTemplate],
        stage_contracts: Optional[Dict[str, Dict[str, Any]]] = None,
        execution_guidance: Optional[Dict[str, Dict[str, Any]]] = None,
        model_effort_guidance: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self._templates_by_edge: Dict[Tuple[str, str], TransitionTemplate] = {}
        self._templates_by_id: Dict[str, TransitionTemplate] = {}
        self._capability_to_edges: Dict[str, List[Tuple[str, str]]] = {}
        self._stage_contracts = dict(stage_contracts or {})
        self._execution_guidance = dict(execution_guidance or {})
        self._model_effort_guidance = dict(model_effort_guidance or {})

        for t in templates:
            edge = (t.from_state, t.to_state)
            if edge in self._templates_by_edge:
                raise TransitionRegistryError(f"Duplicate edge in templates: {edge}")
            if t.transition_id in self._templates_by_id:
                raise TransitionRegistryError(f"Duplicate transition_id: {t.transition_id}")

            self._templates_by_edge[edge] = t
            self._templates_by_id[t.transition_id] = t

            for cap in t.capabilities_released:
                self._capability_to_edges.setdefault(cap, []).append(edge)

    def __len__(self) -> int:
        return len(self._templates_by_edge)

    def get_template(self, from_state: str, to_state: str) -> Optional[TransitionTemplate]:
        return self._templates_by_edge.get((from_state, to_state))

    def get_template_by_id(self, transition_id: str) -> Optional[TransitionTemplate]:
        return self._templates_by_id.get(transition_id)

    def get_all_templates(self) -> List[TransitionTemplate]:
        return list(self._templates_by_edge.values())

    def get_all_edges(self) -> Set[Tuple[str, str]]:
        return set(self._templates_by_edge.keys())

    def get_all_edges_with_proof(self) -> List[Tuple[str, str, str, int]]:
        """(from, to, authorized_actor, requires_proof 0/1) per edge; synced into valid_transitions."""
        return [
            (from_s, to_s, tmpl.authorized_actor, 1 if tmpl.requires_cryptographic_proof else 0)
            for (from_s, to_s), tmpl in self._templates_by_edge.items()
        ]

    def proof_required_edges(self) -> frozenset:
        """The edges whose template declares requires_cryptographic_proof (the single source of truth)."""
        return frozenset(edge for edge, tmpl in self._templates_by_edge.items() if tmpl.requires_cryptographic_proof)

    def get_all_edges_with_actor(self) -> List[Tuple[str, str, str]]:
        """Same edges as get_all_edges(), paired with each template's derived
        authorized_actor. Added for auth-ciba-poc-transition-mechanics (T1);
        kept separate from get_all_edges() to avoid changing that method's
        existing return shape for its one existing caller."""
        return [
            (from_s, to_s, tmpl.authorized_actor)
            for (from_s, to_s), tmpl in self._templates_by_edge.items()
        ]

    def get_all_declared_check_ids(self) -> Set[str]:
        check_ids: Set[str] = set()
        for t in self._templates_by_edge.values():
            for c in t.deterministic_checks:
                check_ids.add(c)
        return check_ids

    def get_edges_releasing_capability(self, capability: str) -> List[Tuple[str, str]]:
        return list(self._capability_to_edges.get(capability, []))

    def get_legal_next_states(self, state: str) -> List[str]:
        """Return legal next states from the canonical state machine.

        This deliberately does not read a YAML-maintained next-state list. Guidance
        may explain an edge, but it must never become a second source of transition
        authority.
        """
        return list(ALLOWED_TRANSITIONS.get(state, []))

    def get_transition_guidance(
        self,
        from_state: str,
        to_state: Optional[str] = None,
        task_id_placeholder: str = "<task-id>",
    ) -> Dict[str, Any]:
        """Build a read-only, advisory snapshot for a state or requested edge."""
        legal_next_states = self.get_legal_next_states(from_state)
        transitions = []
        for next_state in legal_next_states:
            template = self.get_template(from_state, next_state)
            if template is None:
                continue
            transitions.append(self._edge_guidance(template, task_id_placeholder))

        result: Dict[str, Any] = {
            "advisory": True,
            "registry_version": TRANSITION_GUIDANCE_SCHEMA_VERSION,
            "current_state": from_state,
            "stage_contract": self.get_stage_contract(from_state),
            "legal_next_states": legal_next_states,
            "transitions": transitions,
            "execution_guidance": {
                unit: dict(self._execution_guidance[unit])
                for unit in EXECUTION_GUIDANCE_UNITS
            },
            "model_effort_guidance": {
                phase: dict(settings)
                for phase, settings in self._model_effort_guidance.items()
            },
        }
        if to_state is None:
            return result

        if to_state not in legal_next_states:
            result.update({
                "requested_to_state": to_state,
                "legal": False,
                "command": None,
                "denial_guidance": (
                    f"{from_state} -> {to_state} is not a legal transition. "
                    f"Choose one of: {', '.join(legal_next_states) or '(none — terminal state)'}."
                ),
                "recovery_states": legal_next_states,
            })
            return result

        edge = self.get_template(from_state, to_state)
        result.update(self._edge_guidance(edge, task_id_placeholder))
        result["requested_to_state"] = to_state
        result["legal"] = True
        return result

    @staticmethod
    def _edge_guidance(template: TransitionTemplate, task_id_placeholder: str) -> Dict[str, Any]:
        if template.requires_cryptographic_proof:
            command = (
                "python3 plugins/agent-agentic-os/scripts/agent_control.py "
                f"coordinate-transition --task-id {task_id_placeholder} --to {template.to_state} "
                "--interactive --key <path-to-signing-key>"
            )
        elif template.authorized_actor == AUTHORIZED_ACTOR_HUMAN_ONLY:
            command = (
                "python3 plugins/agent-agentic-os/scripts/agent_control.py "
                f"coordinate-transition --task-id {task_id_placeholder} --to {template.to_state} --interactive"
            )
        else:
            command = (
                "python3 plugins/agent-agentic-os/scripts/agent_control.py "
                f"coordinate-transition --task-id {task_id_placeholder} --to {template.to_state} "
                "--human-confirmed 'HUMAN-CONFIRMED: <quote>'"
            )
        configured = dict(template.guidance or {})
        helpers = list(configured.get("helper_commands", []))
        if template.approval.get("required"):
            helpers.append(
                "python3 plugins/agent-agentic-os/scripts/agent_control.py "
                f"record-human-approval --task-id {task_id_placeholder} --approver <name>"
            )
        run_by, basis, why = classify_edge(template)
        return {
            "from_state": template.from_state,
            "to_state": template.to_state,
            "transition_id": template.transition_id,
            "execution_class": run_by,
            "execution_instruction": EXECUTION_CLASS_INSTRUCTIONS[run_by],
            "command": command,
            "helper_commands": helpers,
            "success_guidance": configured.get("success", template.next_steps_hint),
            "denial_guidance": configured.get("denial", template.denial_message),
            "failure_recovery": template.failure_recovery,
        }

    def get_stage_contract(self, state: str) -> Optional[Dict[str, Any]]:
        """Return the entry-question contract for a lifecycle state."""
        return self._stage_contracts.get(state)

    def get_stage_question(self, state: str, question_id: str) -> Optional[Dict[str, Any]]:
        """Return a baseline or adaptive question by ID from a stage contract."""
        contract = self.get_stage_contract(state)
        if not contract:
            return None
        questions = list(contract.get("entry_questions", []))
        for rule in contract.get("adaptive_follow_up_rules", []):
            questions.extend(rule.get("questions", []))
        return next((q for q in questions if q.get("question_id") == question_id), None)

    @classmethod
    def load_from_file(cls, path: Path) -> "TransitionRegistry":
        if not path.exists():
            raise TransitionRegistryError(f"Transition templates file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise TransitionRegistryError(f"Failed to parse YAML from {path}: {e}") from e

        if not isinstance(data, dict) or "templates" not in data:
            raise TransitionRegistryError(f"YAML root must be a dict containing 'templates': {path}")

        raw_templates = data["templates"]
        if not isinstance(raw_templates, list):
            raise TransitionRegistryError(f"'templates' in {path} must be a list")

        raw_stages = data.get("stages", {})
        if not isinstance(raw_stages, dict):
            raise TransitionRegistryError("'stages' in YAML must be a mapping")

        stage_contracts: Dict[str, Dict[str, Any]] = {}
        for state, contract in raw_stages.items():
            if state not in CANONICAL_STATES:
                raise TransitionRegistryError(f"Unknown stage contract state: {state}")
            if not isinstance(contract, dict):
                raise TransitionRegistryError(f"Stage contract for '{state}' must be a mapping")
            for field in ("purpose", "question_policy", "entry_questions", "adaptive_follow_up_rules", "exit_requirements"):
                if field not in contract:
                    raise TransitionRegistryError(f"Stage '{state}' missing required field '{field}'")
            if contract["question_policy"] != "one_at_a_time":
                raise TransitionRegistryError(
                    f"Stage '{state}' must use question_policy 'one_at_a_time'"
                )
            for field in ("entry_questions", "adaptive_follow_up_rules", "exit_requirements"):
                if not isinstance(contract[field], list):
                    raise TransitionRegistryError(f"Stage '{state}' field '{field}' must be a list")
            stage_contracts[state] = contract

        raw_execution_guidance = data.get("execution_guidance")
        if not isinstance(raw_execution_guidance, dict):
            raise TransitionRegistryError("YAML root must contain an 'execution_guidance' mapping")
        execution_guidance: Dict[str, Dict[str, Any]] = {}
        for unit in EXECUTION_GUIDANCE_UNITS:
            contract = raw_execution_guidance.get(unit)
            if not isinstance(contract, dict):
                raise TransitionRegistryError(
                    f"execution_guidance must define mapping for '{unit}'"
                )
            if contract.get("advisory") is not True:
                raise TransitionRegistryError(
                    f"execution_guidance.{unit}.advisory must be true"
                )
            if contract.get("required_fields") != list(EXECUTION_GUIDANCE_FIELDS):
                raise TransitionRegistryError(
                    f"execution_guidance.{unit}.required_fields must match the execution guidance contract"
                )
            if not isinstance(contract.get("instruction"), str) or not contract["instruction"].strip():
                raise TransitionRegistryError(
                    f"execution_guidance.{unit}.instruction must be a non-empty string"
                )
            execution_guidance[unit] = contract

        raw_model_effort_guidance = data.get("model_effort_guidance", {})
        if not isinstance(raw_model_effort_guidance, dict):
            raise TransitionRegistryError("'model_effort_guidance' must be a mapping")
        model_effort_guidance: Dict[str, Dict[str, Any]] = {}
        for phase, settings in raw_model_effort_guidance.items():
            if not isinstance(settings, dict):
                raise TransitionRegistryError(f"model_effort_guidance.{phase} must be a mapping")
            for field in ("recommended_model", "recommended_effort", "reason"):
                if not isinstance(settings.get(field), str) or not settings[field].strip():
                    raise TransitionRegistryError(
                        f"model_effort_guidance.{phase}.{field} must be a non-empty string"
                    )
            if settings.get("requires_confirmation_for_premium") is not True:
                raise TransitionRegistryError(
                    f"model_effort_guidance.{phase}.requires_confirmation_for_premium must be true"
                )
            model_effort_guidance[phase] = settings

        parsed: List[TransitionTemplate] = []
        for idx, raw_item in enumerate(raw_templates):
            if not isinstance(raw_item, dict):
                raise TransitionRegistryError(f"Template at index {idx} must be a mapping")

            # Wildcard expansion fans out into one literal template per canonical state.
            # The reset-to-INTAKE wildcard excludes INTAKE's no-op self-loop.
            if raw_item.get("from_state") == "*":
                base_transition_id = raw_item.get("transition_id", f"wildcard_{idx}")
                wildcard_to_state = raw_item.get("to_state")
                existing_edges = {(t.from_state, t.to_state) for t in parsed}
                expanded_items = []
                for state in CANONICAL_STATES:
                    if state == wildcard_to_state:
                        continue
                    if (state, wildcard_to_state) in existing_edges:
                        continue
                    expanded = dict(raw_item)
                    expanded["from_state"] = state
                    expanded["transition_id"] = f"{base_transition_id}__from_{state}"
                    expanded_items.append(expanded)
            else:
                expanded_items = [raw_item]

            for item in expanded_items:
                for field in REQUIRED_TEMPLATE_FIELDS:
                    if field not in item:
                        raise TransitionRegistryError(f"Missing required field '{field}' in template index {idx}")

                if not isinstance(item["checklist"], list) or len(item["checklist"]) == 0:
                    raise TransitionRegistryError(f"Field 'checklist' must be a non-empty list in template '{item.get('transition_id')}'")
                if not isinstance(item["required_artifacts"], list):
                    raise TransitionRegistryError(f"Field 'required_artifacts' must be a list in template '{item.get('transition_id')}'")
                if not isinstance(item["deterministic_checks"], list):
                    raise TransitionRegistryError(f"Field 'deterministic_checks' must be a list in template '{item.get('transition_id')}'")
                if not isinstance(item["human_questions"], list):
                    raise TransitionRegistryError(f"Field 'human_questions' must be a list in template '{item.get('transition_id')}'")
                for question in item["human_questions"]:
                    if not isinstance(question, dict):
                        raise TransitionRegistryError(
                            f"Human question must be a mapping in template '{item.get('transition_id')}'"
                        )
                    asked_when = question.get("asked_when")
                    if asked_when is not None:
                        earlier = [q.get("question_id") for q in item["human_questions"]]
                        if (not isinstance(asked_when, dict) or set(asked_when) != {"question_id", "answer_contains"}
                                or asked_when["question_id"] not in earlier[:earlier.index(question.get("question_id"))]):
                            raise TransitionRegistryError(
                                f"Field 'asked_when' must be {{question_id, answer_contains}} naming an EARLIER question in template '{item.get('transition_id')}'"
                            )
                    choices_from = question.get("choices_from")
                    if choices_from is not None:
                        earlier_ids = [q.get("question_id") for q in item["human_questions"]]
                        runtime_qid = choices_from.get("runtime_question") if isinstance(choices_from, dict) else None
                        if (not isinstance(choices_from, dict) or choices_from.get("kind") not in ("runtime", "model", "effort")
                                or set(choices_from) - {"kind", "runtime_question"}
                                or (choices_from["kind"] != "runtime" and runtime_qid not in earlier_ids[:earlier_ids.index(question.get("question_id"))])):
                            raise TransitionRegistryError(
                                f"Field 'choices_from' must be {{kind: runtime|model|effort[, runtime_question: <earlier question id>]}} in template '{item.get('transition_id')}'"
                            )
                    accepted_answers = question.get("accepted_answers")
                    if accepted_answers is not None:
                        if not isinstance(accepted_answers, list) or not accepted_answers:
                            raise TransitionRegistryError(
                                f"Field 'accepted_answers' must be a non-empty list in template '{item.get('transition_id')}'"
                            )
                        options = question.get("options", [])
                        if not isinstance(options, list) or any(answer not in options for answer in accepted_answers):
                            raise TransitionRegistryError(
                                f"Field 'accepted_answers' must contain only declared options in template '{item.get('transition_id')}'"
                            )
                if not isinstance(item["approval"], dict):
                    raise TransitionRegistryError(f"Field 'approval' must be a dict in template '{item.get('transition_id')}'")
                if not isinstance(item["skip"], dict):
                    raise TransitionRegistryError(f"Field 'skip' must be a dict in template '{item.get('transition_id')}'")
                if not isinstance(item.get("authority"), dict):
                    raise TransitionRegistryError(f"Field 'authority' must be a dict in template '{item.get('transition_id')}'")
                if not isinstance(item["capabilities_released"], list):
                    raise TransitionRegistryError(f"Field 'capabilities_released' must be a list in template '{item.get('transition_id')}'")
                if not isinstance(item["capabilities_prohibited"], list):
                    raise TransitionRegistryError(f"Field 'capabilities_prohibited' must be a list in template '{item.get('transition_id')}'")
                if not isinstance(item["denial_message"], str) or len(item["denial_message"]) == 0:
                    raise TransitionRegistryError(f"Field 'denial_message' must be a non-empty string in template '{item.get('transition_id')}'")
                if not isinstance(item.get("next_steps_hint"), str) or len(item["next_steps_hint"].strip()) == 0:
                    raise TransitionRegistryError(f"Field 'next_steps_hint' must be a non-empty string in template '{item.get('transition_id')}'")
                if not isinstance(item.get("failure_recovery", ""), str):
                    raise TransitionRegistryError(f"Field 'failure_recovery' must be a string in template '{item.get('transition_id')}'")
                if not isinstance(item.get("stage_question_ids", []), list):
                    raise TransitionRegistryError(f"Field 'stage_question_ids' must be a list in template '{item.get('transition_id')}'")
                if item.get("stage_route") is not None and not isinstance(item["stage_route"], dict):
                    raise TransitionRegistryError(f"Field 'stage_route' must be a mapping in template '{item.get('transition_id')}'")
                if item.get("guidance") is not None and not isinstance(item["guidance"], dict):
                    raise TransitionRegistryError(f"Field 'guidance' must be a mapping in template '{item.get('transition_id')}'")
                guidance = item.get("guidance", {})
                if not isinstance(guidance.get("helper_commands", []), list):
                    raise TransitionRegistryError(
                        f"Field 'guidance.helper_commands' must be a list in template '{item.get('transition_id')}'"
                    )
                for guidance_field in ("success", "denial"):
                    if guidance_field in guidance and not isinstance(guidance[guidance_field], str):
                        raise TransitionRegistryError(
                            f"Field 'guidance.{guidance_field}' must be a string in template '{item.get('transition_id')}'"
                        )

                t = TransitionTemplate(
                    transition_id=item["transition_id"],
                    from_state=item["from_state"],
                    to_state=item["to_state"],
                    purpose=item["purpose"],
                    checklist=item["checklist"],
                    required_artifacts=item["required_artifacts"],
                    deterministic_checks=item["deterministic_checks"],
                    human_questions=item["human_questions"],
                    approval=item["approval"],
                    skip=item["skip"],
                    authority=item["authority"],
                    capabilities_released=item["capabilities_released"],
                    capabilities_prohibited=item["capabilities_prohibited"],
                    denial_message=item["denial_message"],
                    next_steps_hint=item.get("next_steps_hint", ""),
                    failure_recovery=item.get("failure_recovery", ""),
                    stage_question_ids=item.get("stage_question_ids", []),
                    stage_route=item.get("stage_route"),
                    guidance=item.get("guidance", {}),
                    requires_cryptographic_proof=bool(item.get("requires_cryptographic_proof", False)),
                )
                if "requires_cryptographic_proof" in item and not isinstance(item["requires_cryptographic_proof"], bool):
                    raise TransitionRegistryError(
                        f"Field 'requires_cryptographic_proof' must be a boolean in template '{item.get('transition_id')}'"
                    )
                parsed.append(t)

        return cls(parsed, stage_contracts, execution_guidance, model_effort_guidance)

    @classmethod
    def default_path(cls) -> Path:
        return Path(__file__).resolve().parent / "transition_templates.yaml"

    @classmethod
    def default_source_digest(cls) -> str:
        """sha256 of the default YAML's bytes: the cache key for load_default() and an input to the
        persistence adapter's schema-sync fingerprint. Cheap (a file read + hash), unlike a parse."""
        try:
            return hashlib.sha256(cls.default_path().read_bytes()).hexdigest()
        except OSError as e:
            raise TransitionRegistryError(f"Transition templates file not found: {cls.default_path()}") from e

    @classmethod
    def load_default(cls) -> "TransitionRegistry":
        """The default registry, parsed at most once per distinct YAML content in this process.

        Parsing the 158KB YAML with the pure-Python loader costs ~0.13s and load_default() sits on every
        persistence call's path, so it is memoized on the file's content hash (an edited YAML is a new key,
        never stale). The returned instance is shared: treat it as read-only -- nothing in the repo mutates
        a loaded registry, and callers needing a variant build one via load_from_file()."""
        key = cls.default_source_digest()
        cached = _DEFAULT_REGISTRY_CACHE.get(key)
        if cached is None:
            cached = cls.load_from_file(cls.default_path())
            _DEFAULT_REGISTRY_CACHE.clear()  # only the current content is ever reachable
            _DEFAULT_REGISTRY_CACHE[key] = cached
        return cached
