#!/usr/bin/env python
"""
copilot-run-agent (CLI)
=====================================

Purpose:
    Orchestrates a Copilot CLI sub-agent execution by assembling a persona,
    input context, and instruction for specific model invocation.

Layer: Codify

Usage Examples:
    python./scripts/run_agent.py agents/security-auditor.md target.py output.md "Review this."
    ./scripts/run_agent.py agents/refactor-expert.md main.py refactor.md "Optimize logic."

Supported Object Types:
    - Markdown (Persona prompts)
    - Python, JS, TS, C#, etc. (Source code inputs)
    - Text-based documentation

CLI Arguments:
    - persona_file: Path to the markdown file containing the agent persona.
    - input_file: Path to the source code or text file to be analyzed.
    - output_file: Path where the agent's analysis will be saved.
    - instruction: A specific instruction string for the sub-task.

Input Files:
    - Persona markdown files (from agents/ directory)
    - Source code files for analysis

Output:
    - Analysis markdown files (customizable via output_file arg)

Key Functions:
    - resolve_path(): Handles relative path lookup for personas.
    - run_agent(): Main orchestration routine for CLI invocation.

Script Dependencies:
    - subprocess
    - os
    - sys
    - tempfile

Consumed by:
    - Antigravity AI Agent
    - CLI users in the agent-plugins-skills ecosystem
"""

import sys
import os
import subprocess
import tempfile

# --- PATH RESOLUTION ---
def resolve_path(provided_path: str) -> str:
    """
    Resolves the provided file path against the current working directory,
    falling back to the plugin's root (one level up from this script's directory).

    Args:
        provided_path: The file path provided by the user (relative or absolute).

    Returns:
        The resolved absolute or relative path that exists on disk.
    """
    # 1. Try relative to CWD
    if os.path.exists(provided_path):
        return provided_path
    
    # 2. Try resolving relative to the script's directory (Plugin Root)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_root = os.path.dirname(script_dir)
    fallback_path = os.path.join(plugin_root, provided_path)
    
    if os.path.exists(fallback_path):
        return fallback_path
        
    return provided_path

# --- AGENT ORCHESTRATION ---
def run_agent(persona_file: str, input_file: str, output_file: str, instruction: str, model: str = "gpt-5-mini") -> None:
    """
    Orchestrates a Copilot CLI sub-agent execution by assembling a combined prompt.

    Args:
        persona_file: Path to the persona markdown file.
        input_file: Path to the input source file.
        output_file: Path to save the resulting analysis.
        instruction: Specific task instruction for the model.
        model: AI model to use (defaults to gpt-5-mini).

    Raises:
        FileNotFoundError: If the persona or input files cannot be resolved.
        subprocess.CalledProcessError: If the copilot CLI execution fails.
    """
    persona_path = resolve_path(persona_file)
    input_path = resolve_path(input_file)

    try:
        with open(persona_path, 'r') as f:
            persona_content = f.read()
        with open(input_path, 'r') as f:
            input_content = f.read()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Note: For Copilot, we must ensure the prompt string is passed correctly.
    # Prepend a newline to prevent the CLI from misinterpreting a prompt starting with '---' as a flag.
    # We enforce sub-agent isolation in the final combined prompt.
    prompt = (
        f"\n{persona_content}\n\n"
        f"---SOURCE---\n{input_content}\n\n"
        f"---INSTRUCTION---\n{instruction}\n\n"
        "You are operating as an isolated sub-agent. Do NOT use tools. "
        "Do NOT access filesystem. Only use the provided input."
    )

    # Use a temporary file for the prompt to avoid shell argument length limits
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
        tf.write(prompt)
        prompt_tmp_path = tf.name

    try:
        # Run Copilot CLI in non-interactive mode
        # --yolo ensures all tool permissions are granted for headless execution
        cmd = ["copilot", "--yolo", "--model", model, "-p", prompt]
        
        with open(output_file, 'w') as out:
            subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, check=True)
        
        print(f"Agent execution complete. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Copilot CLI: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(prompt_tmp_path):
            os.remove(prompt_tmp_path)

if __name__ == "__main__":
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print("Usage: pythonrun_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> \"<INSTRUCTION>\" [MODEL_NAME]")
        sys.exit(1)
    
    model_name = sys.argv[5] if len(sys.argv) == 6 else "gpt-5-mini"
    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], model_name)
