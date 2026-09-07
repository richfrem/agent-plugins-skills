"""
control_plane/registry.py — TransitionRegistry Domain Component (issue-529 Slice 1)
=====================================================================================

Purpose:
    Loads, schema-validates, and serves the single authoritative transition registry
    (), enforcing 1:1 bidirectional parity with
    state_machine.ALLOWED_TRANSITIONS (51 total edges).

Layer:
    OS Kernel / Execution Control Plane Substrate — Registry (domain layer)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

from control_plane.state_machine import ALLOWED_TRANSITIONS


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
]


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
        }


class TransitionRegistry:
    """Authoritative registry for all transition templates loaded from YAML."""

    def __init__(self, templates: List[TransitionTemplate]):
        self._templates_by_edge: Dict[Tuple[str, str], TransitionTemplate] = {}
        self._templates_by_id: Dict[str, TransitionTemplate] = {}
        self._capability_to_edges: Dict[str, List[Tuple[str, str]]] = {}

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

        parsed: List[TransitionTemplate] = []
        for idx, item in enumerate(raw_templates):
            if not isinstance(item, dict):
                raise TransitionRegistryError(f"Template at index {idx} must be a mapping")

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
            )
            parsed.append(t)

        return cls(parsed)

    @classmethod
    def load_default(cls) -> "TransitionRegistry":
        default_path = Path(__file__).resolve().parent / "transition_templates.yaml"
        return cls.load_from_file(default_path)
