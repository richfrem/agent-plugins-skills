#!/usr/bin/env python3
"""
conductor.py — DEPRECATED
=========================
Purpose:
    Use run_agent.py instead. conductor.py predates the multi-backend run_agent.py router
    and supports only claude/copilot/gemini via adapter classes. run_agent.py covers all
    backends (claude, copilot, agy, codex, llama, gemini) with a unified argparse interface,
    hub-and-spoke symlinks into each skill, and 76+ tests.

    This file is retained for backward compatibility only. Do not add new functionality here.

Key Input Dependencies:
    - path_security.py module (path containment enforcement)
    - adapters/claude_adapter.py, adapters/copilot_adapter.py, adapters/gemini_adapter.py
"""

import os
import sys
import argparse
import tempfile
import subprocess
from pathlib import Path

# Path containment imports
from path_security import assert_under_allowed_roots

# Adapter imports
from adapters.claude_adapter import ClaudeAdapter
from adapters.copilot_adapter import CopilotAdapter
from adapters.gemini_adapter import GeminiAdapter

def get_allowed_roots() -> list[Path]:
    """Return the list of directories allowed for file access (cwd, tmp, optional CLI config dirs)."""
    roots = [
        Path(os.getcwd()).resolve(),
        Path(tempfile.gettempdir()).resolve()
    ]
    # Add optional OS/agent config paths if they exist
    claude_path = Path(os.path.expanduser("~")) / ".claude"
    if claude_path.exists():
        roots.append(claude_path.resolve())
    gemini_path = Path(os.path.expanduser("~")) / ".gemini"
    if gemini_path.exists():
        roots.append(gemini_path.resolve())
    return roots

def read_file_or_empty(path_str: str, allowed_roots: list[Path]) -> str:
    """Read a file's contents if it's under an allowed root, else return an empty string."""
    if path_str in ("/dev/null", "nul", ""):
        return ""
    
    path = Path(path_str)
    try:
        resolved = assert_under_allowed_roots(path, allowed_roots)
        if not resolved.exists() or not resolved.is_file():
            return ""
        return resolved.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning reading path '{path_str}': {e}", file=sys.stderr)
        return ""

def build_prompt(persona_content: str, input_content: str, instruction: str, isolated: bool) -> str:
    """Assemble the full prompt from persona/input/instruction, with an optional isolation footer."""
    parts = []
    has_persona = bool(persona_content.strip())
    has_input = bool(input_content.strip())
    has_instruction = bool(instruction.strip())

    if has_persona:
        parts.append(persona_content)

    if has_input:
        parts.append(f"---SOURCE---\n{input_content}" if has_persona else input_content)

    if has_instruction:
        label = "---INSTRUCTION---\n" if (has_persona or has_input) else ""
        parts.append(f"{label}{instruction}")

    if isolated:
        parts.append(
            "You are operating as an isolated sub-agent. "
            "Do NOT use tools. Do NOT access filesystem. Only use the provided input."
        )

    return "\n\n".join(["\n"] + parts)

def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for conductor.py."""
    parser = argparse.ArgumentParser(description="CLI Agent Conductor")
    parser.add_argument("--backend", required=True, choices=["claude", "copilot", "gemini"])
    parser.add_argument("--persona", default="/dev/null")
    parser.add_argument("--input", default="/dev/null")
    parser.add_argument("--output", required=True)
    parser.add_argument("--instruction", required=True)
    parser.add_argument("--model", default=None)
    # Default to isolated=True (secure by default)
    parser.add_argument("--isolated", action="store_true", default=True)
    parser.add_argument("--allow-tools", dest="isolated", action="store_false", help="Explicitly approve tool usage")
    return parser


def _select_adapter(backend: str):
    """Return the adapter instance for the given backend name."""
    if backend == "claude":
        return ClaudeAdapter()
    if backend == "copilot":
        return CopilotAdapter()
    return GeminiAdapter()


def _write_prompt_tmp(prompt: str) -> str:
    """Write prompt to a new temp file with 0600 permissions and return its path."""
    # We manually manage the creation to apply chmod cleanly
    fd, prompt_tmp_path = tempfile.mkstemp(suffix=".txt", prefix="cli_agent_prompt_")
    os.close(fd)
    os.chmod(prompt_tmp_path, 0o600)
    with open(prompt_tmp_path, 'w', encoding="utf-8") as f:
        f.write(prompt)
    return prompt_tmp_path


def _build_adapter_cmd(adapter, backend: str, prompt: str, prompt_tmp_path: str, model, isolated: bool) -> list:
    """Build the backend CLI command via the adapter (claude takes prompt directly; others take a file path)."""
    if backend == "claude":
        # Claude takes prompt content directly
        return adapter.build_command(prompt, model, isolated)
    # Copilot/Gemini can read prompt from file path
    return adapter.build_command(prompt_tmp_path, model, isolated)


def _run_backend_command(cmd: list, resolved_out: Path, backend: str) -> None:
    """Run the backend CLI command, streaming output to stdout and the output file. Exits on failure."""
    with open(resolved_out, 'w', encoding="utf-8") as out_f:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            out_f.write(line)
        proc.wait()

    if proc.returncode != 0:
        print(f"Error: Backend CLI '{backend}' exited with code {proc.returncode}", file=sys.stderr)
        sys.exit(proc.returncode)


def main():
    """Parse CLI arguments and delegate the task to the selected legacy adapter backend."""
    args = _build_arg_parser().parse_args()

    allowed_roots = get_allowed_roots()

    # Resolve output path safety
    out_path = Path(args.output)
    try:
        resolved_out = assert_under_allowed_roots(out_path, allowed_roots)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Read persona and input files safely
    persona_content = read_file_or_empty(args.persona, allowed_roots)
    input_content = read_file_or_empty(args.input, allowed_roots)

    adapter = _select_adapter(args.backend)
    prompt = build_prompt(persona_content, input_content, args.instruction, args.isolated)

    prompt_tmp_path = None
    try:
        prompt_tmp_path = _write_prompt_tmp(prompt)
        cmd = _build_adapter_cmd(adapter, args.backend, prompt, prompt_tmp_path, args.model, args.isolated)

        # Ensure parent output directory exists
        resolved_out.parent.mkdir(parents=True, exist_ok=True)

        print(f"[*] Running CLI Conductor delegating to backend '{args.backend}' (isolated={args.isolated})...")
        _run_backend_command(cmd, resolved_out, args.backend)

        # Sanity check output
        if resolved_out.stat().st_size == 0:
            print("Error: Output file is empty.", file=sys.stderr)
            sys.exit(1)

        print(f"[+] Agent execution complete. Output saved to {args.output}")

    finally:
        if prompt_tmp_path and os.path.exists(prompt_tmp_path):
            try:
                os.remove(prompt_tmp_path)
            except OSError:
                pass

if __name__ == "__main__":
    main()
