---
concept: split-markdown-lines-into-frontmatter-lines-and-body-lines-around-----delimiters
source: plugin-code
source_file: agent-scaffolders/scripts/validate_agent.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.841824+00:00
cluster: print
content_hash: a672ed09298978c8
---

# Split markdown lines into frontmatter lines and body lines around --- delimiters

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
    pythonvalidate_agent.py <path/to/agent.md>
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
            print("⚠️  description should includ

*(content truncated)*

## See Also

- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[parse-frontmatter-and-content]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/validate_agent.py`
- **Indexed:** 2026-04-27T05:21:03.841824+00:00
