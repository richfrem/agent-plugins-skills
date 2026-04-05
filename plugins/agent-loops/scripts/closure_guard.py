#!/usr/bin/env python3
"""
closure_guard.py
=====================================

Purpose:
    Stop-hook that blocks premature agent session exit when an active learning
    loop is in progress. Reads .claude/agent-loop-state.local.md, parses YAML
    frontmatter, and emits a JSON `block` decision until the closure sequence
    (Seal → Persist → Retrospective) is completed and `closure_done: true` is set.

Layer: Investigate

Usage:
    echo '<hook-json>' | python3 closure_guard.py
"""
import sys
import json
import re
import os

LOOP_STATE_FILE = ".claude/agent-loop-state.local.md"


# Parse simple key: value YAML frontmatter between the two --- delimiters
def parse_frontmatter(content: str) -> dict:
    """
    Extract YAML frontmatter key-value pairs from a markdown string.

    Supports only simple `key: value` lines; nested YAML is not parsed.

    Args:
        content: Full file contents including frontmatter delimiters.

    Returns:
        Dictionary mapping frontmatter keys to their string values.
    """
    lines = content.splitlines()
    in_fm = False
    fm_count = 0
    result: dict = {}
    for line in lines:
        if line.strip() == "---":
            fm_count += 1
            in_fm = fm_count == 1
            if fm_count == 2:
                in_fm = False
            continue
        if in_fm:
            m = re.match(r'^(\w+):\s*(.*)', line)
            if m:
                result[m.group(1)] = m.group(2).strip()
    return result


# Extract the body text that follows the closing --- of the frontmatter block
def get_body(content: str) -> str:
    """
    Return the content section that follows the closing `---` delimiter.

    Args:
        content: Full file contents including frontmatter delimiters.

    Returns:
        Everything after the second `---` line, joined with newlines.
    """
    lines = content.splitlines()
    dash_count = 0
    body: list[str] = []
    for line in lines:
        if line.strip() == "---":
            dash_count += 1
            continue
        if dash_count >= 2:
            body.append(line)
    return "\n".join(body)


# Entry point: enforce closure protocol as a Claude Code Stop hook
def main() -> None:
    """
    Enforce loop closure before allowing agent session exit.

    Reads the JSON hook payload from stdin (required by the hook protocol),
    checks .claude/agent-loop-state.local.md for an active loop, and outputs
    a JSON `block` decision if `closure_done` is not `true`.

    Raises:
        SystemExit: Always exits with code 0 (hook protocol requirement).
    """
    # Consume hook input from stdin (required by hook protocol)
    _ = sys.stdin.read()

    if not os.path.isfile(LOOP_STATE_FILE):
        sys.exit(0)  # No active loop — allow exit

    with open(LOOP_STATE_FILE) as f:
        content = f.read()

    fm = parse_frontmatter(content)
    iteration_str = fm.get("iteration", "")
    max_iterations_str = fm.get("max_iterations", "")
    closure_done = fm.get("closure_done", "")
    pattern = fm.get("pattern", "")

    if closure_done == "true":
        os.remove(LOOP_STATE_FILE)
        sys.exit(0)

    if not re.match(r'^\d+$', iteration_str):
        print(json.dumps({
            "decision": "block",
            "reason": "Corrupted state file.",
            "systemMessage": (
                f"⚠️  Agent loop: State file corrupted "
                f"(iteration: '{iteration_str}'). Please fix the state file."
            ),
        }))
        sys.exit(0)

    iteration = int(iteration_str)

    if (re.match(r'^\d+$', max_iterations_str) and
            int(max_iterations_str) > 0 and
            iteration >= int(max_iterations_str)):
        max_iter = int(max_iterations_str)
        print(json.dumps({
            "decision": "block",
            "reason": "Max iterations reached.",
            "systemMessage": (
                f"🛑 Agent loop: Max iterations ({max_iter}) reached. "
                f"Forcing closure.\n\n"
                f"You MUST still complete the closure sequence:\n"
                f"1. Seal (bundle session artifacts)\n"
                f"2. Persist (append session traces)\n"
                f"3. Retrospective (analyze what went right/wrong)\n"
                f"4. Set closure_done: true in '{LOOP_STATE_FILE}'"
            ),
        }))
        sys.exit(0)

    # Closure not done — block exit and increment iteration
    prompt_text = get_body(content)
    next_iteration = iteration + 1

    new_content = re.sub(
        r'^iteration: .*',
        f'iteration: {next_iteration}',
        content,
        flags=re.MULTILINE,
    )
    tmp_path = f"{LOOP_STATE_FILE}.tmp.{os.getpid()}"
    with open(tmp_path, "w") as f:
        f.write(new_content)
    os.replace(tmp_path, LOOP_STATE_FILE)

    print(json.dumps({
        "decision": "block",
        "reason": prompt_text,
        "systemMessage": (
            f"🔄 Agent loop iteration {next_iteration} ({pattern}) | "
            f"Closure NOT complete — you must Seal → Persist → Retrospective before exiting."
        ),
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
