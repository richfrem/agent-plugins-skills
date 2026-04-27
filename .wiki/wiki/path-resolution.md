---
concept: path-resolution
source: plugin-code
source_file: claude-cli/scripts/run_agent.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.241071+00:00
cluster: agent
content_hash: 87a6d2a54096375f
---

# --- PATH RESOLUTION ---

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/claude-cli/scripts/run_agent.py -->
#!/usr/bin/env python
"""
claude-run-agent (CLI)
=====================================

Purpose:
    Orchestrates a Claude CLI sub-agent execution by assembling a persona,
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

Consumed by:
    - Antigravity AI Agent
    - CLI users in the agent-plugins-skills ecosystem
"""

import sys
import subprocess
import os

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
def run_agent(persona_file: str, input_file: str, output_file: str, instruction: str) -> None:
    """
    Orchestrates a Claude CLI sub-agent execution by assembling a combined prompt.

    Args:
        persona_file: Path to the persona markdown file.
        input_file: Path to the input source file.
        output_file: Path to save the resulting analysis.
        instruction: Specific task instruction for the model.

    Raises:
        FileNotFoundError: If the persona or input files cannot be resolved.
        subprocess.CalledProcessError: If the claude CLI execution fails.
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

    # Note: For Claude, we must ensure the prompt string is passed correctly.
    # Prepend a newline to prevent the CLI from misinterpreting a prompt starting with '---' as a flag.
    # We enforce sub-agent isolation in the final combined prompt.
    prompt = (
        f"\n{persona_content}\n\n"
        f"---SOURCE---\n{input_content}\n\n"
        f"---INSTRUCTION---\n{instruction}\n\n"
        "You are operating as an isolated sub-agent. Do NOT use tools. "
        "Do NOT access filesystem. Only use the provided input."
    )

    # Use haiku-4.5 as the default efficient model for Claude CLI
    cmd = ["claude", "--model", "haiku-4.5", "-p", prompt]

    try:
        with open(output_file, 'w') as out:
            

*(content truncated)*

<!-- Source: plugin-code/gemini-cli/scripts/run_agent.py -->
#!/usr/bin/env python
"""
gemini-run-agent (CLI)
=====================================

Purpose:
    Orchestrates a Gemini CLI sub-agent execution by assembling a persona,
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
    - instruction: A specif

*(combined content truncated)*

## See Also

- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[broken-path-string]]
- [[non-whitelistable-python-runtime-path-construction]]
- [[path-bootstrap]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `claude-cli/scripts/run_agent.py`
- **Indexed:** 2026-04-27T05:21:04.241071+00:00
