#!/usr/bin/env python3
"""
Generate Eval Instructions
=====================================

Purpose:
    Generates the eval-instructions.md file for a target skill evaluation lab
    by rendering a template file with the provided skill metadata and paths.

Layer: Investigate / Codify / Curate / Retrieve
    Codify

Usage:
    python generate_eval_instructions.py --template <path> --out <path> [args]
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any

# Generates evaluation instructions from a template
def generate_instructions(template_path: str, out_path: str, replacements: Dict[str, str]) -> None:
    """
    Reads the eval template, substitutes all variable placeholders, and writes to output.

    Args:
        template_path: Absolute or relative path to the source template file.
        out_path: Destination path for the rendered instruction markdown.
        replacements: Dictionary of template placeholders mapped to their final values.

    Returns:
        None

    Raises:
        FileNotFoundError: If the source template_path does not exist.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)
        
    for key, value in replacements.items():
        content = content.replace(key, value)
        
    out_file = Path(out_path)
    # Ensure the destination directory exists
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(content)


def main() -> None:
    """
    Parses CLI arguments, prepares the replacements dictionary, and triggers generation.
    """
    parser = argparse.ArgumentParser(description="Generate eval-instructions.md from a template")
    parser.add_argument("--template", required=True, help="Path to the template file")
    parser.add_argument("--out", required=True, help="Output path for eval-instructions.md")
    
    # Placeholders map
    parser.add_argument("--skill-display-name", required=True, help="Human readable skill name")
    parser.add_argument("--skill-name", required=True, help="Canonical skill folder name")
    parser.add_argument("--plugin-dir", required=True, help="Plugin directory name")
    parser.add_argument("--mutation-target", required=True, help="Target file for mutation (e.g. SKILL.md)")
    parser.add_argument("--repo-url", required=True, help="GitHub clone URL for the lab repo")
    parser.add_argument("--round-label", required=True, help="Short label for run logs")
    parser.add_argument("--engine-source", required=True, help="Absolute path to installed os-eval-runner")
    parser.add_argument("--master-plugin-path", required=True, help="Absolute path to the master plugin")
    
    args = parser.parse_args()
    
    replacements: Dict[str, str] = {
        '{{SKILL_DISPLAY_NAME}}': args.skill_display_name,
        '{{SKILL_NAME}}': args.skill_name,
        '{{PLUGIN_DIR}}': args.plugin_dir,
        '{{MUTATION_TARGET}}': args.mutation_target,
        '{{GITHUB_REPO_URL}}': args.repo_url,
        '{{ROUND_LABEL}}': args.round_label,
        '{{SKILL_EVAL_SOURCE}}': args.engine_source,
        '{{MASTER_PLUGIN_PATH}}': args.master_plugin_path
    }
    
    generate_instructions(args.template, args.out, replacements)
    print(f"Successfully generated {args.out}")


if __name__ == '__main__':
    main()
