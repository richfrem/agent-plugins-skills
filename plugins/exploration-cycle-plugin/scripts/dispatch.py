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
import re
import subprocess
import os
import sys

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


def main() -> None:
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
    parser.add_argument("--tier", default="1", choices=["1", "2", "3"],
                        help="Risk tier (1=low, 2=moderate, 3=high). Tier 2/3 require human gate "
                             "before bash-capable dispatch. Only Tier 1 uses --dangerously-skip-permissions. "
                             "Default: 1 (backward compatible).")

    args = parser.parse_args()

    # 1. Read the agent instructions and strip YAML frontmatter.
    # Frontmatter (---\n...\n---) is metadata, not instructions. Passing it verbatim
    # to CLI tools that treat --- as an argument delimiter (e.g. claude) causes parse failures.
    agent_content = read_file(args.agent)
    agent_content = re.sub(r'^---[\r\n]+.*?[\r\n]+---[\r\n]+', '', agent_content, count=1, flags=re.DOTALL)

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
