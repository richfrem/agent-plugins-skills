#!/usr/bin/env python
"""
closure_guard.py
=====================================

Purpose:
    Stop-hook that blocks premature agent session exit when an active learning
    loop is in progress. Reads .claude/agent-loop-state.local.md, parses YAML
    frontmatter, and emits a JSON `block` decision until the closure sequence
    (Seal → Persist → Retrospective) is completed and `closure_done: true` is set.

Key Input Dependencies:
    - .claude/agent-loop-state.local.md (learning loop state file with YAML frontmatter)
    - Hook JSON input via stdin (Claude Code hook protocol)
    - PyYAML library (for frontmatter parsing)

Key Functions:
    - parse_frontmatter(): Extract YAML frontmatter from markdown file
    - check_closure_done(): Check if loop is ready for session exit

Layer: Investigate

Usage:
    echo '<hook-json>' | python closure_guard.py
"""
import sys
import json
import re
import os
import fcntl

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

LOOP_STATE_FILE = ".claude/agent-loop-state.local.md"


# Parse YAML frontmatter using pyyaml for correctness (handles comments, quotes, types)
def parse_frontmatter(content: str) -> dict:
    """
    Extract YAML frontmatter key-value pairs from a markdown string.

    Uses yaml.safe_load for correct handling of comments, quoted values, and booleans.

    Args:
        content: Full file contents including frontmatter delimiters.

    Returns:
        Dictionary mapping frontmatter keys to their parsed values.
    """
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


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


def _handle_closure_done(fm: dict) -> None:
    """If closure_done is set, remove the state file and exit 0 (allow session exit)."""
    closure_done = fm.get("closure_done", False)
    # yaml.safe_load parses 'true' as bool True; treat both bool True and str 'true'
    if closure_done is True or str(closure_done).lower() == "true":
        os.remove(LOOP_STATE_FILE)
        sys.exit(0)


def _block_if_corrupted(iteration_str: str) -> None:
    """Emit a block decision and exit if the iteration field is non-numeric (corrupted state)."""
    if re.match(r'^\d+$', iteration_str):
        return
    print(json.dumps({
        "decision": "block",
        "reason": "Corrupted state file.",
        "systemMessage": (
            f"⚠️  Agent loop: State file corrupted "
            f"(iteration: '{iteration_str}'). Please fix the state file."
        ),
    }))
    sys.exit(0)


def _block_if_max_iterations(iteration: int, max_iterations_str: str) -> None:
    """Emit a block decision and exit if max_iterations has been reached."""
    if not (re.match(r'^\d+$', max_iterations_str) and
            int(max_iterations_str) > 0 and
            iteration >= int(max_iterations_str)):
        return
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


def _increment_iteration_locked() -> tuple:
    """Acquire an exclusive lock, increment the iteration field, and return (next_iteration, content).

    Prevents TOCTOU races when multiple hook invocations fire concurrently.
    """
    with open(LOOP_STATE_FILE, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        content = f.read()
        fm = parse_frontmatter(content)  # re-parse under lock for freshness
        iteration_str = fm.get("iteration", "0")
        if not re.match(r'^\d+$', str(iteration_str)):
            iteration_str = "0"
        next_iteration = int(iteration_str) + 1
        new_content = re.sub(
            r'^iteration: .*',
            f'iteration: {next_iteration}',
            content,
            flags=re.MULTILINE,
        )
        tmp_path = f"{LOOP_STATE_FILE}.tmp.{os.getpid()}"
        with open(tmp_path, "w") as tmp:
            tmp.write(new_content)
        os.replace(tmp_path, LOOP_STATE_FILE)
        # fcntl lock released on f.close() via context manager
    return next_iteration, content


def _emit_continue_block(next_iteration: int, pattern: str, prompt_text: str) -> None:
    """Emit the block decision instructing the agent to continue the closure sequence."""
    print(json.dumps({
        "decision": "block",
        "reason": prompt_text,
        "systemMessage": (
            f"🔄 Agent loop iteration {next_iteration} ({pattern}) | "
            f"Closure NOT complete — you must Seal → Persist → Retrospective before exiting."
        ),
    }))
    sys.exit(0)


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
    _handle_closure_done(fm)

    iteration_str = fm.get("iteration", "")
    max_iterations_str = fm.get("max_iterations", "")
    pattern = fm.get("pattern", "")

    _block_if_corrupted(iteration_str)
    iteration = int(iteration_str)
    _block_if_max_iterations(iteration, max_iterations_str)

    # Closure not done — acquire exclusive lock, increment iteration, release
    next_iteration, content = _increment_iteration_locked()
    prompt_text = get_body(content)

    _emit_continue_block(next_iteration, pattern, prompt_text)


if __name__ == "__main__":
    main()
