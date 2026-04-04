#!/usr/bin/env python3
import sys
import subprocess
import os

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
    Orchestrates a Gemini CLI sub-agent execution by assembling a persona,
    input context, and instruction for specific model invocation.
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

    # Note: For Gemini, we must ensure the prompt string is passed correctly.
    # Prepend a newline to prevent the CLI from misinterpreting a prompt starting with '---' as a flag
    prompt = f"\n{persona_content}\n\n---SOURCE---\n{input_content}\n\n---INSTRUCTION---\n{instruction}\n\nYou are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

    # Use -m gemini-3-flash-preview for maximum speed and token efficiency
    cmd = ["gemini", "-m", "gemini-3-flash-preview", "-p", prompt]

    try:
        with open(output_file, 'w') as out:
            # We redirect model output to the file
            subprocess.run(cmd, stdout=out, check=True)
            
        print(f"Gemini Agent execution complete. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Gemini CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> \"<INSTRUCTION>\"")
        sys.exit(1)
    
    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
