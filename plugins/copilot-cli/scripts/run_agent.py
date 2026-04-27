#!/usr/bin/env python
"""
copilot-run-agent (CLI)
=====================================

Purpose:
    Orchestrates a Copilot CLI sub-agent execution by assembling a persona,
    input context, and instruction for specific model invocation.

Layer: Codify

Usage Examples:
    # Task dispatch (agent uses filesystem tools — default behaviour):
    python scripts/run_agent.py /dev/null tasks/todo/my_prompt.md temp/out.md \
        "Implement all changes." claude-sonnet-4.6

    # Analysis only (isolated, no tools):
    python scripts/run_agent.py agents/security-auditor.md target.py output.md \
        "Review this." gpt-5-mini false

    # Heartbeat check:
    python scripts/run_agent.py /dev/null /dev/null temp/hb.md \
        "HEARTBEAT CHECK: Respond with HEARTBEAT_OK only."

Prompt assembly rules:
    - persona present + input present  → persona / ---SOURCE--- input / ---INSTRUCTION--- instruction
    - input present, no persona        → input / ---INSTRUCTION--- instruction  (task-dispatch mode)
    - instruction only (both /dev/null)→ instruction only
    - isolated=true appends:          "You are operating as an isolated sub-agent. Do NOT use tools."

CLI Arguments:
    persona_file  Path to agent persona markdown, or /dev/null to skip.
    input_file    Path to task prompt or source file, or /dev/null to skip.
    output_file   Path where output is saved (streamed live to stdout as well).
    instruction   Specific task instruction string.
    model         AI model identifier (default: gpt-5-mini).
    isolated      "true" to block tool use; default "false". Pass explicitly when
                  running analysis-only tasks where filesystem writes are unsafe.

Script Dependencies:
    subprocess, os, sys, tempfile

Consumed by:
    - Antigravity AI Agent
    - CLI users in the agent-plugins-skills ecosystem
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


def build_prompt(persona_content: str, input_content: str, instruction: str, isolated: bool) -> str:
    """
    Assemble the final prompt from available parts.

    Three modes:
      - Full (persona + input): persona / ---SOURCE--- input / ---INSTRUCTION--- instruction
      - Task dispatch (input only): input / ---INSTRUCTION--- instruction
      - Instruction only (heartbeat etc.): instruction
    """
    parts = []

    has_persona = bool(persona_content.strip())
    has_input = bool(input_content.strip())
    has_instruction = bool(instruction.strip())

    if has_persona:
        parts.append(persona_content)

    if has_input:
        # Wrap in SOURCE block only when a persona is also present
        parts.append(f"---SOURCE---\n{input_content}" if has_persona else input_content)

    if has_instruction:
        label = "---INSTRUCTION---\n" if (has_persona or has_input) else ""
        parts.append(f"{label}{instruction}")

    if isolated:
        parts.append(
            "You are operating as an isolated sub-agent. "
            "Do NOT use tools. Do NOT access filesystem. Only use the provided input."
        )

    # Leading newline prevents CLI from misinterpreting a prompt starting with '---' as a flag
    return "\n\n".join(["\n"] + parts)


def run_agent(
    persona_file: str,
    input_file: str,
    output_file: str,
    instruction: str,
    model: str = "gpt-5-mini",
    isolated: bool = False,
) -> None:
    """
    Orchestrate a Copilot CLI sub-agent execution.

    Args:
        persona_file: Persona markdown path, or /dev/null to skip.
        input_file:   Task prompt / source file path, or /dev/null to skip.
        output_file:  Path where output is saved.
        instruction:  Task instruction string.
        model:        Copilot model identifier.
        isolated:     When True, appends isolation footer blocking tool use.
                      Default False — agent may use filesystem tools via --yolo.
    """
    persona_content = read_file_or_empty(resolve_path(persona_file))
    input_content = read_file_or_empty(resolve_path(input_file))

    prompt = build_prompt(persona_content, input_content, instruction, isolated)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
        tf.write(prompt)
        prompt_tmp_path = tf.name

    try:
        if sys.platform == "win32":
            ps_script = (
                f'$p = Get-Content -Raw "{prompt_tmp_path}"; '
                f'copilot --yolo --model {model} -p $p'
            )
            cmd = ["powershell", "-NoProfile", "-Command", ps_script]
        else:
            cmd = ["copilot", "--yolo", "--model", model, "-p", f"@{prompt_tmp_path}"]

        # Stream output live to stdout and write to output_file simultaneously
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, 'w') as out_f:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                out_f.write(line)
            proc.wait()

        if proc.returncode != 0:
            print(f"Error: copilot exited with code {proc.returncode}")
            sys.exit(proc.returncode)

        print(f"Agent execution complete. Output saved to {output_file}")
    finally:
        if os.path.exists(prompt_tmp_path):
            os.remove(prompt_tmp_path)


if __name__ == "__main__":
    if len(sys.argv) < 5 or len(sys.argv) > 7:
        print(
            "Usage: run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "
            '"<INSTRUCTION>" [MODEL] [isolated=false]'
        )
        sys.exit(1)

    _model = sys.argv[5] if len(sys.argv) >= 6 else "gpt-5-mini"
    _isolated = sys.argv[6].lower() == "true" if len(sys.argv) == 7 else False
    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], _model, _isolated)
