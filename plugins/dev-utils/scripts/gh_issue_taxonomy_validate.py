#!/usr/bin/env python3
"""GitHub Issue Taxonomy Validator.

Purpose:
  Validates label selections against issue-taxonomy.json, ensuring mandatory location labels (area:* or plugin:*).

Key Input Dependencies:
  - issue-taxonomy.json (machine-readable taxonomy schema)

Usage:
  python gh_issue_taxonomy_validate.py [label1] [label2] ...
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_taxonomy_validate

import json
import os
import sys
from typing import Dict, List, Optional, Tuple


def load_taxonomy(json_path: Optional[str] = None) -> Dict:
    """Load the machine-readable taxonomy JSON file."""
    if not json_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "issue-taxonomy.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_taxonomy(labels: List[str], taxonomy_path: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Validate list of labels against taxonomy rules.

    Args:
        labels: List of label strings to validate.
        taxonomy_path: Optional path to issue-taxonomy.json override.

    Returns:
        Tuple of (is_valid, list_of_error_strings).
    """
    tax = load_taxonomy(taxonomy_path)
    errors: List[str] = []
    found_dims = set()
    has_location = False

    for label in labels:
        matched = False
        for dim, values in tax["dimensions"].items():
            if label in values:
                found_dims.add(dim)
                matched = True
                if dim == "area":
                    has_location = True
                break
        if not matched and label.startswith(tax["plugin_prefix"]):
            found_dims.add("plugin")
            has_location = True
            matched = True
        if not matched:
            errors.append(f"Unrecognized label: '{label}'")

    for req in tax["required_dimensions"]:
        if req not in found_dims:
            errors.append(f"Missing required dimension: '{req}'")

    if not has_location:
        errors.append("Missing required location (area:* or plugin:*) label")

    return (len(errors) == 0, errors)


if __name__ == "__main__":
    valid, errs = validate_taxonomy(sys.argv[1:])
    if not valid:
        print("Taxonomy Validation Failed:", errs)
        sys.exit(1)
    print("Taxonomy Validated Successfully")
