#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile

def resolve_path(provided_path):
    """
    Resolves the provided file path against the current working directory,
    falling back to the plugin's root (one level up from this script's directory).
    """
    if os.path.exists(provided_path):
        return provided_path
    
    # Try resolving relative to the script's directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_root = os.path.dirname(script_dir)
    fallback_path = os.path.join(plugin_root, provided_path)
    
    if os.path.exists(fallback_path):
        return fallback_path
        
    return provided_path

def run_agent(persona_file, input_file, output_file, instruction):
    """
    Orchestrates a Copilot CLI sub-agent execution by assembling a persona,
    input context, and instruction into a single prompt for non-interactive execution.
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

    # Assemble the prompt exactly as per the formalized pattern
    # Prepend a newline to prevent the CLI from misinterpreting a prompt starting with '---' as a flag
    prompt = f"\n{persona_content}\n\n---SOURCE---\n{input_content}\n\n---INSTRUCTION---\n{instruction}\n\nYou are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

    # Use a temporary file for the prompt to avoid shell argument length limits
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
        tf.write(prompt)
        prompt_tmp_path = tf.name

    try:
        # Run Copilot CLI in non-interactive mode
        # --yolo ensures all tool permissions are granted for headless execution
        cmd = ["copilot", "--yolo", "-p", prompt]
        
        with open(output_file, 'w') as out:
            subprocess.run(cmd, stdout=out, check=True)
        
        print(f"Agent execution complete. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Copilot CLI: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(prompt_tmp_path):
            os.remove(prompt_tmp_path)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> \"<INSTRUCTION>\"")
        sys.exit(1)
    
    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
