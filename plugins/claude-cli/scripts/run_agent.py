#!/usr/bin/env python3
import sys
import subprocess
import os

def run_agent(persona_file, input_file, output_file, instruction):
    """
    Orchestrates a Claude CLI sub-agent execution by assembling a persona,
    input context, and instruction for specific model invocation.
    """
    try:
        with open(persona_file, 'r') as f:
            persona_content = f.read()
            
        with open(input_file, 'r') as f:
            input_content = f.read()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Note: For Claude, we must ensure the prompt string is passed correctly.
    # Prepend a newline to prevent the CLI from misinterpreting a prompt starting with '---' as a flag
    prompt = f"\n{persona_content}\n\n---SOURCE---\n{input_content}\n\n---INSTRUCTION---\n{instruction}\n\nYou are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

    # Use haiku-4.5 as the default efficient model for Claude CLI
    cmd = ["claude", "--model", "haiku-4.5", "-p", prompt]

    try:
        with open(output_file, 'w') as out:
            # We redirect model output to the file
            subprocess.run(cmd, stdout=out, check=True)
            
        print(f"Claude Agent execution complete. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Claude CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> \"<INSTRUCTION>\"")
        sys.exit(1)
    
    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
