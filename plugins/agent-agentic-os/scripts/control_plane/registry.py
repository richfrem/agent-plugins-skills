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
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

from control_plane.state_machine import ALLOWED_TRANSITIONS, CANONICAL_STATES


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
    stage_question_ids: List[str] = None
    stage_route: Optional[Dict[str, Any]] = None
    guidance: Optional[Dict[str, Any]] = None

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
            "stage_question_ids": list(self.stage_question_ids or []),
            "stage_route": dict(self.stage_route or {}),
            "guidance": dict(self.guidance or {}),
        }


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
        command = (
            "python3 plugins/agent-agentic-os/scripts/agent_control.py "
            f"coordinate-transition --task-id {task_id_placeholder} --to {template.to_state}"
        )
        configured = dict(template.guidance or {})
        helpers = list(configured.get("helper_commands", []))
        if template.approval.get("required"):
            helpers.append(
                "python3 plugins/agent-agentic-os/scripts/agent_control.py "
                f"record-human-approval --task-id {task_id_placeholder} --approver <name>"
            )
        return {
            "from_state": template.from_state,
            "to_state": template.to_state,
            "transition_id": template.transition_id,
            "command": command,
            "helper_commands": helpers,
            "success_guidance": configured.get("success", template.next_steps_hint),
            "denial_guidance": configured.get("denial", template.denial_message),
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
                    stage_question_ids=item.get("stage_question_ids", []),
                    stage_route=item.get("stage_route"),
                    guidance=item.get("guidance", {}),
                )
                parsed.append(t)

        return cls(parsed, stage_contracts, execution_guidance, model_effort_guidance)

    @classmethod
    def load_default(cls) -> "TransitionRegistry":
        default_path = Path(__file__).resolve().parent / "transition_templates.yaml"
        return cls.load_from_file(default_path)
