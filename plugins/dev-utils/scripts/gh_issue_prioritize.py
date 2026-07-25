#!/usr/bin/env python3
"""
GitHub Issue Prioritizer Engine
===============================
Purpose:
    Ranks GitHub issues (P0-P3) based on friction tier, frequency of occurrence,
    and blockages, generating GitHub Projects v2 custom field payloads for sync.

Layer: Domain Logic / Curation
Key Input Dependencies:
    - Issue metadata dicts (labels, occurrence counts, body)
    - GitHub Projects v2 IDs (project, item, field, option)
"""

from typing import List, Dict, Any, Tuple, Optional


def calculate_priority(
    friction_tier: int = 0,
    frequency: int = 1,
    is_blocking: bool = False
) -> Tuple[str, int]:
    """Calculates priority rating (P0, P1, P2, P3) and numeric score.

    Args:
        friction_tier: Tier rating from 0 to 3 (3 being systemic/critical).
        frequency: Number of observed occurrences of the issue/friction.
        is_blocking: True if the issue blocks work or execution.

    Returns:
        Tuple of (priority_label, numeric_score).
        - P0: Critical / Systemic (Tier 3 OR (Blocking AND frequency >= 3))
        - P1: High priority (Tier 2 OR Blocking OR frequency >= 4)
        - P2: Medium priority (Tier 1 OR frequency >= 2)
        - P3: Low priority / Backlog (Default)
    """
    # Calculate score
    score = (friction_tier * 30) + (frequency * 10) + (40 if is_blocking else 0)

    if friction_tier >= 3 or (is_blocking and frequency >= 3) or score >= 90:
        return "P0", max(score, 100)
    elif friction_tier == 2 or is_blocking or frequency >= 4 or score >= 60:
        return "P1", score
    elif friction_tier == 1 or frequency >= 2 or score >= 30:
        return "P2", score
    else:
        return "P3", score


def extract_friction_tier(labels: List[Any]) -> int:
    """Extracts friction tier number from labels list.

    Accepts both bare (`tier:3`) and this repo's taxonomy-suffixed form
    (`tier:3-architecture`, per issue-taxonomy.json) by reading only the
    leading digit run after the colon.
    """
    tier = 0
    for label in labels:
        name = label.get("name", "") if isinstance(label, dict) else str(label)
        if name.startswith("tier:"):
            digits = ""
            for ch in name.split(":", 1)[1]:
                if ch.isdigit():
                    digits += ch
                else:
                    break
            if digits:
                tier = max(tier, int(digits))
    return tier


def check_is_blocking(labels: List[Any], title: str = "", body: str = "") -> bool:
    """Checks if issue is marked as blocking via label or text content."""
    for label in labels:
        name = label.get("name", "") if isinstance(label, dict) else str(label)
        if name.lower() in ("blocking", "blocker", "type:blocker", "severity:blocking"):
            return True

    text = f"{title} {body}".lower()
    return "blocks execution" in text or "blocking work" in text or "hard block" in text


def prioritize_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Processes a raw issue dictionary and appends priority calculations.

    Args:
        issue: Issue dictionary containing labels, number, title, occurrence_count, etc.

    Returns:
        Dictionary containing priority summary and issue metadata.
    """
    labels = issue.get("labels", [])
    title = issue.get("title", "")
    body = issue.get("body", "")

    friction_tier = extract_friction_tier(labels)
    is_blocking = check_is_blocking(labels, title, body)
    frequency = issue.get("occurrence_count", 1)

    priority, score = calculate_priority(
        friction_tier=friction_tier,
        frequency=frequency,
        is_blocking=is_blocking
    )

    return {
        "issue_number": issue.get("number"),
        "title": title,
        "priority": priority,
        "priority_score": score,
        "priority_label": f"priority:{priority}",
        "friction_tier": friction_tier,
        "is_blocking": is_blocking,
        "frequency": frequency
    }


def generate_projects_v2_payload(
    project_id: str,
    item_id: str,
    field_id: str,
    single_select_option_id: str
) -> Dict[str, Any]:
    """Generates GraphQL mutation payload for updating Projects v2 Single Select custom field.

    Args:
        project_id: GitHub Projects v2 Node ID (e.g. PVT_...)
        item_id: Project Item Node ID (e.g. PVTI_...)
        field_id: Field Node ID (e.g. PVTF_...)
        single_select_option_id: Option ID corresponding to P0/P1/P2/P3 option.

    Returns:
        GraphQL request dict containing query string and variables dict.
    """
    query = """mutation UpdateProjectV2ItemValue($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: {
        singleSelectOptionId: $optionId
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}"""
    return {
        "query": query,
        "variables": {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "value": {
                "singleSelectOptionId": single_select_option_id
            }
        }
    }
