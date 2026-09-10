"""Validation for the machine-readable implementation task ledger."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


LEDGER_HEADING = "## Implementation Task Ledger"


def _load_entries(plan_path: Path) -> list[Dict[str, Any]]:
    text = plan_path.read_text(encoding="utf-8")
    heading_start = text.find(LEDGER_HEADING)
    if heading_start < 0:
        raise ValueError(f"{plan_path.name} is missing the '{LEDGER_HEADING}' section")
    fenced_start = text.find("```json", heading_start)
    if fenced_start < 0:
        raise ValueError(f"{plan_path.name} ledger must contain a fenced JSON block")
    payload_start = fenced_start + len("```json")
    fenced_end = text.find("```", payload_start)
    if fenced_end < 0:
        raise ValueError(f"{plan_path.name} ledger JSON block is not closed")
    entries = json.loads(text[payload_start:fenced_end].strip())
    if not isinstance(entries, list) or not entries:
        raise ValueError("implementation ledger must be a non-empty JSON list")
    if not all(isinstance(entry, dict) for entry in entries):
        raise ValueError("every implementation ledger entry must be a JSON object")
    return entries


def validate_implementation_ledger(plan_path: Path, repo_root: Path) -> Optional[str]:
    """Return a denial reason unless every planned implementation item is proven complete."""
    try:
        entries = _load_entries(plan_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return f"Implementation ledger invalid: {exc}"

    root = repo_root.resolve()
    for entry in entries:
        task_id = str(entry.get("id", "")).strip() or "<unnamed>"
        if entry.get("status") != "COMPLETE":
            return f"Implementation task '{task_id}' is not COMPLETE."
        evidence = entry.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            return f"Implementation task '{task_id}' is missing completion evidence."
        artifacts = entry.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            return f"Implementation task '{task_id}' must list one or more artifacts."
        for artifact in artifacts:
            if not isinstance(artifact, str) or not artifact.strip():
                return f"Implementation task '{task_id}' contains an invalid artifact path."
            candidate = (root / artifact).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                return f"Implementation task '{task_id}' artifact escapes repository root: {artifact}"
            if not candidate.exists():
                return f"Implementation task '{task_id}' artifact is missing: {artifact}"
    return None
