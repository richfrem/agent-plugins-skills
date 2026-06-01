#!/usr/bin/env python
"""
agy-run-agent (CLI)
=====================================

Purpose:
    Orchestrates an Antigravity (agy) CLI sub-agent execution by assembling a
    persona, input context, and instruction for frontier Gemini model invocation.

Usage Examples:
    python ./scripts/run_agent.py agents/security-auditor.md target.py output.md "Review this."
    python ./scripts/run_agent.py /dev/null /dev/null heartbeat.md "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."

CLI Arguments:
    persona_file  Path to agent persona markdown, or /dev/null to skip.
    input_file    Path to task prompt or source file, or /dev/null to skip.
    output_file   Path where output is saved (streamed live to stdout as well).
    instruction   Specific task instruction string.

Script Dependencies:
    subprocess, os, sys, tempfile
"""

import sys
import os
import subprocess
import tempfile


def resolve_path(provided_path: str) -> str:
    """Resolve path against CWD then plugin root, return as-is if neither exists."""
    if os.path.exists(provided_path):
        return provided_path
    script_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_root = os.path.dirname(script_dir)
    fallback = os.path.join(plugin_root, provided_path)
    return fallback if os.path.exists(fallback) else provided_path


def read_file_or_empty(path: str) -> str:
    """Read file content; return empty string for /dev/null or missing files."""
    if path in ("/dev/null", "nul", "") or not os.path.exists(path):
        return ""
    try:
        with open(path, 'r') as f:
            return f.read()
    except (OSError, IOError):
        return ""


def build_prompt(persona_content: str, input_content: str, instruction: str) -> str:
    """Assemble the final prompt from available parts."""
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

    return "\n\n".join(["\n"] + parts)


def run_agent(persona_file: str, input_file: str, output_file: str, instruction: str) -> None:
    """Orchestrate an agy CLI sub-agent execution."""
    persona_content = read_file_or_empty(resolve_path(persona_file))
    input_content = read_file_or_empty(resolve_path(input_file))
    prompt = build_prompt(persona_content, input_content, instruction)

    # Homebrew path injection for native macOS execution
    if os.path.exists("/opt/homebrew/bin") and "/opt/homebrew/bin" not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"

    prompt_tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
            tf.write(prompt)
            prompt_tmp_path = tf.name

        cmd = ["agy", "--dangerously-skip-permissions", "-p", f"@{prompt_tmp_path}"]

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, 'w') as out_f:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in (proc.stdout or []):
                sys.stdout.write(line)
                sys.stdout.flush()
                out_f.write(line)
            proc.wait()

        if proc.returncode != 0:
            print(f"Error: agy exited with code {proc.returncode}")
            sys.exit(proc.returncode)

        print(f"Agent execution complete. Output saved to {output_file}")
    finally:
        if prompt_tmp_path and os.path.exists(prompt_tmp_path):
            os.remove(prompt_tmp_path)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print('Usage: run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>"')
        sys.exit(1)
    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
