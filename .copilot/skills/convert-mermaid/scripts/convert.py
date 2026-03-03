#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

"""
convert.py (CLI)
=====================================

Purpose:
    Converts a mermaid (.mmd/.mermaid) file to a PNG utilizing standard headless integration.

Layer: Tools & Generation

Usage Examples:
    python3 convert.py -i input.mmd -o output.png -s 2 -t dark

Supported Object Types:
    - Mermaid standard (.mmd)
    - PNG binary export

CLI Arguments:
    -i, --input: Input .mmd file
    -o, --output: Output .png file
    -s, --scale: Resolution scale factor (default: 1)
    -t, --theme: Theme variant (default, forest, dark, neutral)

Input Files:
    - Raw text file containing Mermaid syntax.

Output:
    - PNG file.

Key Functions:
    - convert_mermaid(): The subprocess caller wrapping headless execution.

Script Dependencies:
    - npx @mermaid-js/mermaid-cli

Consumed by:
    - User (CLI)
    - convert-mermaid (Agent Skill)
"""

def convert_mermaid(input_file, output_file, scale=1, theme="default"):
    """
    Converts a mermaid (.mmd/.mermaid) file to a PNG using mmdc.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    # Use npx to lazily execute mermaid-cli so the user doesn't need to globally install it
    # We use -y to accept the npx installation prompt if it's the first time
    command = [
        "npx", "-y", "@mermaid-js/mermaid-cli",
        "-i", input_file,
        "-o", output_file,
        "-s", str(scale),
        "-t", theme,
        # Ensure puppeteer works in most environments without complex sandbox setups
        "-p", "puppeteer-config.json" 
    ]
    
    # Create a temporary puppeteer config to bypass sandbox issues on some OSes
    config_path = "puppeteer-config.json"
    with open(config_path, "w") as f:
        f.write('{"args": ["--no-sandbox"]}')

    print(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Success! Diagram saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert diagram. Error:\n{e.stderr}")
        sys.exit(1)
    finally:
        if os.path.exists(config_path):
            os.remove(config_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Mermaid diagrams to PNG with scalable resolution.")
    parser.add_argument("-i", "--input", required=True, help="Input .mmd or .mermaid file")
    parser.add_argument("-o", "--output", required=True, help="Output .png file")
    parser.add_argument("-s", "--scale", type=int, default=1, help="Resolution scale factor (e.g., 2, 3, 4 for higher res/retina)")
    parser.add_argument("-t", "--theme", default="default", choices=["default", "forest", "dark", "neutral"], help="Mermaid theme")
    
    args = parser.parse_args()
    
    convert_mermaid(args.input, args.output, args.scale, args.theme)
