#!/usr/bin/env python
"""
validate_agent.py
=====================================

Purpose:
    Validates a Claude Code agent markdown file for YAML frontmatter structure,
    required fields (name, description, model, color), field format constraints,
    system prompt length and style, and example block presence.

Layer: Investigate

Usage:
    python validate_agent.py <path/to/agent.md>
"""
import sys
import os
import re

_SEPARATOR = "━" * 40
_VALID_MODELS = frozenset({"inherit", "sonnet", "opus", "haiku"})
_VALID_COLORS = frozenset({"blue", "cyan", "green", "yellow", "magenta", "red"})
_GENERIC_NAMES = frozenset({"helper", "assistant", "agent", "tool"})


# Split markdown lines into frontmatter lines and body lines around --- delimiters
def _split_frontmatter(lines: list) -> tuple:
    """
    Split file lines into frontmatter and body sections.

    Args:
        lines: All lines of the markdown file.

    Returns:
        Tuple of (frontmatter_lines, body_lines).
    """
    fm: list = []
    body: list = []
    dash_count = 0
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            dash_count += 1
            in_fm = dash_count == 1
            if dash_count == 2:
                in_fm = False
            continue
        (fm if in_fm else body if dash_count >= 2 else []).append(line)
    return fm, body


# Run all structural and content checks on the agent markdown file
def validate(agent_file: str) -> bool:
    """
    Run all validation checks on the given agent markdown file.

    Args:
        agent_file: Filesystem path to the agent `.md` file.

    Returns:
        True if there are no errors (warnings are tolerated); False otherwise.
    """
    print(f"🔍 Validating agent file: {agent_file}")
    print()

    if not os.path.isfile(agent_file):
        print(f"❌ File not found: {agent_file}")
        return False
    print("✅ File exists")

    with open(agent_file, errors="replace") as fh:
        lines = fh.readlines()

    if not lines or lines[0].strip() != "---":
        print("❌ File must start with YAML frontmatter (---)")
        return False
    print("✅ Starts with frontmatter")

    if not any(ln.strip() == "---" for ln in lines[1:]):
        print("❌ Frontmatter not closed (missing second ---)")
        return False
    print("✅ Frontmatter properly closed")

    fm_lines, body_lines = _split_frontmatter(lines)
    fm = "".join(fm_lines)
    sp = "".join(body_lines)

    errors = 0
    warnings = 0

    print()
    print("Checking required fields...")

    # name
    name_m = re.search(r"^name:\s*(.+)", fm, re.MULTILINE)
    if not name_m:
        print("❌ Missing required field: name")
        errors += 1
    else:
        name = name_m.group(1).strip().strip('"')
        print(f"✅ name: {name}")
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$", name):
            print("❌ name must start/end with alphanumeric; only letters, numbers, hyphens")
            errors += 1
        if len(name) < 3:
            print("❌ name too short (minimum 3 characters)")
            errors += 1
        elif len(name) > 50:
            print("❌ name too long (maximum 50 characters)")
            errors += 1
        if name in _GENERIC_NAMES:
            print(f"⚠️  name is too generic: {name}")
            warnings += 1

    # description
    desc_m = re.search(r"^description:\s*(.+)", fm, re.MULTILINE)
    if not desc_m:
        print("❌ Missing required field: description")
        errors += 1
    else:
        desc = desc_m.group(1).strip()
        print(f"✅ description: {len(desc)} characters")
        if len(desc) < 10:
            print("⚠️  description too short (minimum 10 characters recommended)")
            warnings += 1
        elif len(desc) > 5000:
            print("⚠️  description very long (over 5000 characters)")
            warnings += 1
        if desc.count("<example>") < 2 or desc.count("<example>") > 4:
            print("⚠️  description should include 2-4 <example> blocks for triggering")
            warnings += 1
        if not re.search(r"use this agent when", desc, re.IGNORECASE):
            print("⚠️  description should start with 'Use this agent when...'")
            warnings += 1

    # model
    model_m = re.search(r"^model:\s*(.+)", fm, re.MULTILINE)
    if not model_m:
        print("❌ Missing required field: model")
        errors += 1
    else:
        model = model_m.group(1).strip()
        print(f"✅ model: {model}")
        if model not in _VALID_MODELS:
            print(f"⚠️  Unknown model: {model} (valid: {', '.join(sorted(_VALID_MODELS))})")
            warnings += 1

    # color
    color_m = re.search(r"^color:\s*(.+)", fm, re.MULTILINE)
    if not color_m:
        print("❌ Missing required field: color")
        errors += 1
    else:
        color = color_m.group(1).strip()
        print(f"✅ color: {color}")
        if color not in _VALID_COLORS:
            print(f"⚠️  Unknown color: {color} (valid: {', '.join(sorted(_VALID_COLORS))})")
            warnings += 1

    # tools (optional)
    tools_m = re.search(r"^tools:\s*(.+)", fm, re.MULTILINE)
    if tools_m:
        print(f"✅ tools: {tools_m.group(1).strip()}")
    else:
        print("💡 tools: not specified (agent has access to all tools)")

    # system prompt
    print()
    print("Checking system prompt...")
    sp_stripped = sp.strip()
    if not sp_stripped:
        print("❌ System prompt is empty")
        errors += 1
    else:
        print(f"✅ System prompt: {len(sp)} characters")
        if len(sp) < 20:
            print("❌ System prompt too short (minimum 20 characters)")
            errors += 1
        elif len(sp) > 10000:
            print("⚠️  System prompt very long (over 10,000 characters)")
            warnings += 1
        if not re.search(r"You are|You will|Your", sp):
            print("⚠️  System prompt should use second person (You are..., You will...)")
            warnings += 1
        if not re.search(r"responsibilities|process|steps", sp, re.IGNORECASE):
            print("💡 Consider adding clear responsibilities or process steps")
        if not re.search(r"output", sp, re.IGNORECASE):
            print("💡 Consider defining output format expectations")

    print()
    print(_SEPARATOR)

    if errors == 0 and warnings == 0:
        print("✅ All checks passed!")
        return True
    if errors == 0:
        print(f"⚠️  Validation passed with {warnings} warning(s)")
        return True
    print(f"❌ Validation failed with {errors} error(s) and {warnings} warning(s)")
    return False


# Entry point: validate a single agent markdown file from CLI arguments
def main() -> None:
    """
    Parse CLI args and run agent file validation.

    Raises:
        SystemExit: Code 0 on pass (with or without warnings); code 1 on errors.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path/to/agent.md>")
        print()
        print("Validates agent file for:")
        for item in (
            "YAML frontmatter structure",
            "Required fields (name, description, model, color)",
            "Field formats and constraints",
            "System prompt presence and length",
            "Example blocks in description",
        ):
            print(f"  - {item}")
        sys.exit(1)
    sys.exit(0 if validate(sys.argv[1]) else 1)


if __name__ == "__main__":
    main()
