# -*- coding: utf-8 -*-
"""
validate_github_agent.py
=====================================
Purpose:
    Validates generated GitHub Agent configurations (.agent.md and gh-aw MD).
    Returns JSON findings and exits 0/1.

Key Input Dependencies:
    - PyYAML                    — Used for frontmatter metadata YAML parsing
    - os, sys, re, argparse     — Standard library packages for CLI parsing and path management
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
    """Parse YAML frontmatter blocks and body contents from raw markdown text."""
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


def validate_target_a(fm: dict, body: str, filepath_str: str = "") -> list[str]:
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

    # Poka-yoke: A .agent.md file MUST NOT contain gh-aw keys (on or safe-outputs)
    if "on" in fm or "safe-outputs" in fm:
        errors.append("GitHub agent file (.agent.md) must not contain gh-aw keys ('on' or 'safe-outputs').")

    return errors


def validate_target_b(fm: dict, body: str, filepath_str: str = "") -> list[str]:
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

    # Poka-yoke: workflows/ path checking
    if filepath_str and "/workflows/" in filepath_str and filepath_str.endswith(".md"):
        skill_keys = {"argument-hint", "allowed-tools", "disable-model-invocation"}
        has_skill_keys = any(k in fm for k in skill_keys)
        missing_workflow_keys = "on" not in fm or "engine" not in fm
        if has_skill_keys and missing_workflow_keys:
            errors.append("Skill-style frontmatter in .github/workflows/ — run scaffold_github_agent.py --target B; do not hand-author.")

    return errors


def validate_target_c(fm: dict, body: str, kill_switch: str = None, filepath_str: str = "") -> list[str]:
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

    # Poka-yoke: Target C .agent.md file MUST NOT contain gh-aw keys
    if "on" in fm or "safe-outputs" in fm:
        errors.append("GitHub agent file (.agent.md) must not contain gh-aw keys ('on' or 'safe-outputs').")

    return errors


def main() -> None:
    """CLI entry point: parses target agent path and target type, and runs matching validation checks."""
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
    filepath_str = filepath.resolve().as_posix()
    
    if args.target == "A":
        errors = validate_target_a(fm, body, filepath_str)
    elif args.target == "B":
        errors = validate_target_b(fm, body, filepath_str)
    elif args.target == "C":
        errors = validate_target_c(fm, body, args.kill_switch, filepath_str)
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
