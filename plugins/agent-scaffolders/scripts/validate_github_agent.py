# -*- coding: utf-8 -*-
"""
validate_github_agent.py
=====================================
Purpose:
    Validates generated GitHub Agent configurations (.agent.md and gh-aw MD).
    Returns JSON findings and exits 0/1.
"""

import os
import sys
import re
import argparse
import json
from pathlib import Path
import yaml

# Resolve imports cleanly from the real directory (resolving symlinks)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


def parse_frontmatter(content: str) -> tuple[dict, str]:
    fm = {}
    body = content
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
        except Exception:
            pass
        body = content[match.end():]
        
    # PyYAML boolean trap: YAML 1.1 converts "on" -> True, "off" -> False
    # Normalize these keys back to strings for proper validation
    if fm:
        for bad, good in ((True, "on"), (False, "off")):
            if bad in fm:
                fm[good] = fm.pop(bad)
                
    return fm, body


def validate_target_a(fm: dict, body: str) -> list[str]:
    """
    Validate Target A: Custom Copilot Agent (.agent.md) [GitHub schema, GA]
    """
    errors = []
    # description is REQUIRED
    if "description" not in fm or not str(fm["description"]).strip():
        errors.append("Target A frontmatter must contain a non-empty 'description'.")
    
    # target validation
    if "target" in fm and fm["target"] not in ("vscode", "github-copilot", "both"):
        errors.append(f"Target '{fm['target']}' must be one of 'vscode', 'github-copilot', 'both'.")
        
    # tools must be list if present
    if "tools" in fm and not isinstance(fm["tools"], list):
        errors.append("'tools' field must be a list in Target A.")

    # body size check (max 30,000 chars)
    if len(body) > 30000:
        errors.append(f"Body length ({len(body)} chars) exceeds maximum allowed size of 30,000 chars.")

    return errors


def validate_target_b(fm: dict, body: str) -> list[str]:
    """
    Validate Target B: GitHub Agentic Workflow (gh-aw) [technical preview]
    """
    errors = []
    # 'on' is required
    if "on" not in fm:
        errors.append("Target B frontmatter must contain 'on' triggers.")
        
    # engine validation
    if "engine" in fm and fm["engine"] not in ("copilot", "claude", "codex"):
        errors.append(f"Engine '{fm['engine']}' must be one of 'copilot', 'claude', 'codex'.")
        
    # safe-outputs shape check (must be dict)
    if "safe-outputs" in fm and not isinstance(fm["safe-outputs"], dict):
        errors.append("'safe-outputs' must be a dictionary.")

    return errors


def validate_target_c(fm: dict, body: str, kill_switch: str = None) -> list[str]:
    """
    Validate Target C: CI/CD Smart Failure Agent
    """
    errors = []
    # Check for Kill Switch phrase in body (case-insensitive)
    body_lower = body.lower()
    if kill_switch:
        if kill_switch.lower() not in body_lower:
            errors.append(f"Kill switch phrase '{kill_switch}' must appear verbatim in the body.")
    else:
        # Check if any common kill switch pattern or section exists
        if "kill switch" not in body_lower and "quality gate" not in body_lower:
            errors.append("Smart Failure Agent should define a Kill Switch section in the body.")
            
    # Check for Escalation Trigger Taxonomy (case-insensitive)
    if "escalation trigger taxonomy" not in body_lower:
        errors.append("Smart Failure Agent must define an 'Escalation Trigger Taxonomy' section in the body.")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate GitHub Agent configuration files.")
    parser.add_argument("--file", required=True, help="Path to the file to validate")
    parser.add_argument(
        "--target",
        choices=["A", "B", "C"],
        required=True,
        help="Target type to validate (A: Custom Agent, B: gh-aw, C: Smart Failure)",
    )
    parser.add_argument("--kill-switch", help="Expected kill switch phrase for Target C")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        result = {
            "status": "error",
            "file": args.file,
            "errors": [f"File not found: {args.file}"]
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        result = {
            "status": "error",
            "file": args.file,
            "errors": [f"Failed to read file: {e}"]
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    fm, body = parse_frontmatter(content)
    
    if args.target == "A":
        errors = validate_target_a(fm, body)
    elif args.target == "B":
        errors = validate_target_b(fm, body)
    elif args.target == "C":
        errors = validate_target_c(fm, body, args.kill_switch)
    else:
        errors = ["Unknown target type"]

    result = {
        "status": "fail" if errors else "pass",
        "file": args.file,
        "errors": errors,
        "findings": {
            "frontmatter_keys": list(fm.keys()),
            "body_length": len(body),
        }
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
