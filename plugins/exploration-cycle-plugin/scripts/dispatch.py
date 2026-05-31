#!/usr/bin/env python
"""
dispatch.py (CLI)
=====================================

Purpose:
    Safely dispatches multi-file context to a CLI backend (claude, gh copilot, or copilot)
    using embedded prompting. Replaces brittle Bash string concatenation.
    Default backend: claude (--cli claude). Override with --cli copilot or --cli gh-copilot.

Layer: Infrastructure / Tooling

Usage Examples:
    pythondispatch.py --agent agent.md --context brief.md captures.md --instruction "Mode: run" --output out.md
    pythondispatch.py --agent agent.md --context brief.md --optional-context prototype-notes.md --instruction "Mode: run" --output out.md

Supported Object Types:
    Any text-based plugin artifacts

CLI Arguments:
    --agent: path to the agent markdown file
    --context: one or more paths to required context files (missing = fatal)
    --optional-context: one or more paths to optional context files (missing = silently skipped)
    --instruction: the explicit prompt command for the agent
    --output: file path to save the generated output
    --timeout: subprocess timeout in seconds (default: 120)

Input Files:
    - Agent instructions (.md)
    - Context payload files (.md, .txt)

Output:
    - Target rendered artifact file

Key Functions:
    read_file(): Safe UTF-8 file reading with missing file handling
    read_optional_file(): Reads file if it exists, returns None if missing
    write_file(): Safe target directory creation and UTF-8 file writing
    validate_output(): Checks output is non-empty, has headers, meets minimum length
    main(): Argument parsing and subprocess Copilot orchestration

Script Dependencies:
    subprocess
    os
    sys
    argparse

Consumed by:
    exploration-cycle-orchestrator-agent.md
    exploration-workflow/SKILL.md
"""

import argparse
import fnmatch
import hashlib
import json
import re
import sqlite3
import subprocess
import os
import sys
from collections import OrderedDict
from pathlib import Path

from sandbox_runner import verify_envelope

MIN_OUTPUT_CHARS = 500


def read_file(filepath: str) -> str:
    """Reads a required file. Exits non-zero if missing."""
    if not os.path.exists(filepath):
        print(f"Error: Could not find required file at '{filepath}'", file=sys.stderr)
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def read_optional_file(filepath: str) -> str | None:
    """Reads an optional file. Returns None silently if missing."""
    if not os.path.exists(filepath):
        print(f"Info: Optional file not found, skipping: '{filepath}'")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def write_file(filepath: str, content: str) -> None:
    """Safely writes content to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')


def _strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter only if it starts at byte 0."""
    match = re.match(r'^---[ \t]*\r?\n.*?\r?\n---[ \t]*\r?\n', content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def _detect_frontmatter_injection(content: str) -> bool:
    """Detect YAML-like blocks injected after the document body begins.

    Returns True if a secondary '---' delimiter followed by key: value lines
    is found after the leading frontmatter. Lone horizontal rules are not flagged.
    """
    body = _strip_frontmatter(content)
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "---":
            for rest_line in lines[i + 1:]:
                stripped = rest_line.strip()
                if stripped == "---":
                    break
                if re.match(r'^[A-Za-z][\w-]*\s*:', stripped):
                    return True
                if stripped and not stripped.startswith("#"):
                    break
        i += 1
    return False


def strip_leading_prose(content: str) -> str:
    """Strips conversational preamble before the first markdown section header.

    Claude CLI responses sometimes prepend a natural-language opener
    (e.g. "Here is the audit report:") before the structured document body.
    This trims everything before the first line starting with '#' so that
    validate_output() and the written artifact both start at the document root.

    If no '#' header is found, the original content is returned unchanged so
    that the header-presence check in validate_output() still fires correctly.
    """
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith('#'):
            stripped = ''.join(lines[i:])
            if i > 0:
                print(f"Info: Stripped {i} line(s) of leading prose before first section header.")
            return stripped
    return content


def validate_output(content: str, output_path: str) -> str | None:
    """Validates CLI output before writing to disk.

    Strips leading prose first (conversational openers before the document
    root), then applies three checks:
      1. Output is non-empty.
      2. Output contains at least one markdown section header (#).
      3. Output meets minimum character length (guards against stub/echo responses).

    Returns the (possibly trimmed) content string if valid, False otherwise.
    Callers should use the returned string, not the original, when writing.
    """
    content = strip_leading_prose(content)

    if not content or not content.strip():
        print(f"Error: CLI returned empty output — refusing to write {output_path}", file=sys.stderr)
        return None
    if not any(line.startswith('#') for line in content.splitlines()):
        print(f"Error: CLI output has no section headers — likely truncated or malformed, refusing to write {output_path}", file=sys.stderr)
        return None
    if len(content.strip()) < MIN_OUTPUT_CHARS:
        print(
            f"Error: CLI output is suspiciously short ({len(content.strip())} chars, minimum {MIN_OUTPUT_CHARS}) "
            f"— likely a stub or echo response, refusing to write {output_path}",
            file=sys.stderr,
        )
        return None
    return content


def check_approval(conn: sqlite3.Connection, approval_id: str) -> tuple[bool, str]:
    """Verify an approval is active, not revoked, and not expired."""
    row = conn.execute(
        "SELECT is_active, expires_at < datetime('now') AS is_expired "
        "FROM approvals WHERE id=?",
        (approval_id,)
    ).fetchone()
    if row is None:
        return False, f"Approval '{approval_id}' not found"
    if not row[0]:
        return False, f"Approval '{approval_id}' has been revoked"
    if row[1]:
        return False, f"Approval '{approval_id}' has expired"
    return True, ""


def check_dispatch_authorization(
    conn: sqlite3.Connection,
    approval_id: str,
    action: str,
    target_path: str | None,
    spec_path: str | None,
    envelope: dict,
    key: bytes,
    nonce_cache: OrderedDict,
) -> tuple[bool, str]:
    """Full dispatch authorization: approval validity + action + path + spec hash + HMAC."""
    # 1. Basic approval validity
    is_valid, reason = check_approval(conn, approval_id)
    if not is_valid:
        return False, reason

    row = conn.execute(
        "SELECT approved_actions, allowed_paths, spec_hash FROM approvals WHERE id=?",
        (approval_id,)
    ).fetchone()
    if row is None:
        return False, f"Approval '{approval_id}' disappeared during authorization"

    # 2. Approved actions check
    approved_actions = json.loads(row[0])
    if action not in approved_actions:
        return False, f"Action '{action}' not in approved_actions {approved_actions}"

    # 3. Allowed paths check
    allowed_paths = json.loads(row[1])
    if target_path and not any(fnmatch.fnmatch(target_path, p) for p in allowed_paths):
        return False, f"Path '{target_path}' not in allowed_paths {allowed_paths}"

    # 4. Spec hash integrity check (fail closed when file is absent)
    if spec_path:
        spec_file = Path(spec_path)
        if not spec_file.exists():
            return False, f"Spec file not found: {spec_path}"
        actual_hash = hashlib.sha256(spec_file.read_bytes()).hexdigest()
        if actual_hash != row[2]:
            return False, f"Spec hash mismatch for {spec_path}"

    # 5. HMAC envelope verification (timing-safe + nonce dedup)
    if not verify_envelope(envelope, key, nonce_cache):
        return False, "HMAC envelope verification failed (tampered payload or replayed nonce)"

    return True, ""


def build_agent_index(agents_dir: Path) -> dict[str, Path]:
    """Build alias index: stem, stem-without-agent, frontmatter name: — all → same file."""
    index: dict[str, Path] = {}
    for md_file in sorted(agents_dir.glob("*.md")):
        stem = md_file.stem
        index[stem] = md_file
        if stem.endswith("-agent"):
            index.setdefault(stem[:-6], md_file)
        content = md_file.read_text(encoding="utf-8")
        m = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if m:
            index.setdefault(m.group(1).strip(), md_file)
    return index


def build_handoff_envelope(
    from_agent: str, to_agent: str, reason: str,
    user_message: str, transcript: list[tuple[str, str]],
    turns: int = 8, chars_per_turn: int = 300,
) -> str:
    context = "\n".join(
        f"{role}: {text[:chars_per_turn]}"
        for role, text in transcript[-turns:]
    )
    return (
        f"You are receiving a handoff from {from_agent}.\n"
        f"Reason: {reason}\n\n"
        f"Recent conversation:\n{context}\n\n"
        f"User's latest message: \"{user_message}\"\n\n"
        f"Continue according to your own agent manifest. "
        f"Do not repeat {from_agent}'s intake questions."
    )


def build_parser() -> argparse.ArgumentParser:
    """Return the configured argument parser. Exposed for testing."""
    parser = argparse.ArgumentParser(description="Exploration Cycle CLI Dispatch Wrapper")
    parser.add_argument("--agent", required=True, help="Path to the agent markdown file")
    parser.add_argument("--context", nargs='+', default=[], help="Required context files — missing file is a fatal error")
    parser.add_argument("--optional-context", nargs='+', default=[], dest="optional_context",
                        help="Optional context files — missing files are silently skipped")
    parser.add_argument("--instruction", required=True, help="The instruction passed to the agent")
    parser.add_argument("--output", required=True, help="Path to save the resulting artifact")
    parser.add_argument("--timeout", type=int, default=120, help="Subprocess timeout in seconds (default: 120)")
    parser.add_argument("--cli", default="claude",
                        choices=["claude", "copilot", "gh-copilot"],
                        help="CLI backend to use (default: claude). 'copilot' = GitHub Copilot standalone CLI, 'gh-copilot' = gh copilot suggest.")
    parser.add_argument("--model", default=None,
                        help="Model to use (optional). When --cli copilot, appended as '--model <model>'. "
                             "Example: claude-sonnet-4.6")
    parser.add_argument("--tier", default="2", choices=["1", "2", "3"],
                        help="Risk tier (1=low, 2=moderate, 3=high). Tier 2/3 require human gate "
                             "before bash-capable dispatch. Only Tier 1 uses --dangerously-skip-permissions. "
                             "Default: 2.")
    # Authorization gate arguments (required for secure dispatch)
    parser.add_argument("--db-path", required=True,
        help="Path to active_session.sqlite")
    parser.add_argument("--approval-id", required=True,
        help="UUID of the active approval record in the DB")
    parser.add_argument("--dispatch-action", default="run_agent",
        help="Action being dispatched for allowlist check (default: run_agent)")
    parser.add_argument("--target-path", default=None,
        help="File path target for path allowlist check (optional)")
    parser.add_argument("--spec-path", default=None,
        help="Path to spec document for hash integrity check (optional)")
    parser.add_argument("--envelope-json", required=True,
        help="JSON-serialized HMAC envelope from sandbox_runner.make_envelope()")
    parser.add_argument("--hmac-key-path", required=True,
        help="Path to the session HMAC key file")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    # Authorization gate — fail-closed. No dispatch without valid approval + HMAC.
    from state_engine import init_db
    from sandbox_runner import load_session_key

    conn = init_db(args.db_path)
    key = load_session_key(Path(args.hmac_key_path))
    envelope = json.loads(args.envelope_json)
    nonce_cache: OrderedDict = OrderedDict()

    ok, reason = check_dispatch_authorization(
        conn,
        args.approval_id,
        args.dispatch_action,
        args.target_path,
        args.spec_path,
        envelope,
        key,
        nonce_cache,
    )
    if not ok:
        print(f"Error: dispatch authorization failed: {reason}", file=sys.stderr)
        sys.exit(1)

    # 1. Read the agent instructions and strip YAML frontmatter.
    # Frontmatter (---\n...\n---) is metadata, not instructions. Passing it verbatim
    # to CLI tools that treat --- as an argument delimiter (e.g. claude) causes parse failures.
    agent_content = read_file(args.agent)
    if _detect_frontmatter_injection(agent_content):
        print("Error: Frontmatter injection detected in agent file — failing closed.", file=sys.stderr)
        sys.exit(1)
    agent_content = _strip_frontmatter(agent_content)

    # 2. Read required context files (missing = fatal)
    context_chunks = []
    for ctx_file in args.context:
        context_chunks.append(read_file(ctx_file))

    # 3. Read optional context files (missing = skip)
    for ctx_file in args.optional_context:
        content = read_optional_file(ctx_file)
        if content is not None:
            context_chunks.append(content)

    if len(context_chunks) == 0:
        print("Error: no context was loaded — all required and optional files are missing or empty. "
              "A zero-context dispatch always produces hallucinated output. Aborting.", file=sys.stderr)
        sys.exit(1)

    context_content = "\n\n---\n\n".join(context_chunks)

    # 4. Build the full prompt payload
    full_prompt = f"{agent_content}\n\n---\n\n{context_content}"

    print(f"Dispatching via {args.cli} — agent: {os.path.basename(args.agent)}...")
    print(f"Instruction: {args.instruction}")

    # 5. Build CLI command based on selected backend
    # For claude and gh-copilot, combine everything into one prompt argument.
    # For copilot (GitHub Copilot standalone), use the -p <system> <user> two-arg format.
    combined_prompt = f"{full_prompt}\n\n---\n\nInstruction: {args.instruction}"

    if args.cli == "claude":
        # Security: --dangerously-skip-permissions is only applied for Tier 1 (low risk) dispatches.
        # Tier 2/3 workloads run with standard permissions — the caller must ensure required tool
        # access is granted before dispatch. See references/architecture.md Rigor Tier table.
        cmd = ["claude", "-p", combined_prompt]
        if args.tier == "1":
            cmd.append("--dangerously-skip-permissions")
        else:
            # Tier 2/3: no auto permission bypass — agent runs with standard permissions
            print(f"Info: Tier {args.tier} dispatch — not applying --dangerously-skip-permissions. "
                  f"Ensure required tool permissions are granted interactively.", file=sys.stderr)
    elif args.cli == "gh-copilot":
        cmd = ["gh", "copilot", "suggest", "-t", "shell", combined_prompt]
    else:  # copilot (GitHub Copilot standalone CLI)
        cmd = ["copilot", "-p", full_prompt, args.instruction]
        if args.model:
            cmd = ["copilot", "--model", args.model, "-p", full_prompt, args.instruction]

    # 6. Invoke the CLI
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=args.timeout,
        )
        output_text = result.stdout

        # 7. Validate output before writing (returns trimmed content or False)
        validated = validate_output(output_text, args.output)
        if not validated:
            sys.exit(1)
        assert isinstance(validated, str)

        # 8. Write to output (use validated/trimmed content, not raw output_text)
        write_file(args.output, validated)
        print(f"Success: Wrote artifact to {args.output}")

    except subprocess.TimeoutExpired:
        print(f"Error: {args.cli} timed out after {args.timeout}s — aborting", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error during {args.cli} invocation: {e.stderr}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
