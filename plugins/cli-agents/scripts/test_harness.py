#!/usr/bin/env python3
"""
test_harness.py
===============
Provides manifest validation and a mock execution environment to simulate how
skills run within the Microsoft Agent Framework (MAF).
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path

def validate_maf_plugin(plugin_path: Path) -> bool:
    print(f"[*] Validating MAF compatibility for: {plugin_path}")
    plugin_json_path = plugin_path / ".claude-plugin" / "plugin.json"
    
    if not plugin_json_path.exists():
        print("❌ Error: Missing .claude-plugin/plugin.json manifest.")
        return False
        
    try:
        manifest = json.loads(plugin_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Error: Invalid JSON in manifest: {e}")
        return False

    required_keys = ["name", "version"]
    for key in required_keys:
        if key not in manifest:
            print(f"❌ Error: Missing required manifest key '{key}'.")
            return False

    # Check for banned/unsupported fields in MAF context
    banned_keys = ["skills", "agents", "hooks"]
    for key in banned_keys:
        if key in manifest:
            print(f"⚠️  Warning: Banned key '{key}' found in manifest (ignored by MAF).")

    print("✅ Manifest is fully compatible with MAF.")
    return True

def simulate_maf_run(skill_path: Path, input_file: Path, instruction: str):
    print(f"[*] Simulating MAF execution for skill: {skill_path.name}")
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found at {skill_md}")
        sys.exit(1)

    try:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            print("❌ Error: Missing YAML frontmatter in SKILL.md")
            sys.exit(1)
        
        parts = content.split("---")
        frontmatter = yaml.safe_load(parts[1])
        print(f"[+] Loaded Skill: {frontmatter.get('name')}")
        print(f"[+] Allowed Tools: {frontmatter.get('allowed-tools')}")
    except Exception as e:
        print(f"❌ Error parsing frontmatter: {e}")
        sys.exit(1)

    input_text = ""
    if input_file and input_file.exists():
        input_text = input_file.read_text(encoding="utf-8")

    print("[*] Assembling MAF Execution Frame...")
    print(f"--- INSTRUCTION ---\n{instruction}\n")
    print(f"--- INPUT CONTEXT ({len(input_text)} chars) ---")
    print("[+] Simulated run completed successfully.")

def main():
    parser = argparse.ArgumentParser(description="MAF Local Simulator & Validator")
    parser.add_argument("--validate", action="store_true", help="Validate plugin for MAF compatibility")
    parser.add_argument("--plugin", type=str, help="Path to plugin directory to validate")
    parser.add_argument("--skill", type=str, help="Path to skill directory to simulate")
    parser.add_argument("--input", type=str, help="Path to input context file")
    parser.add_argument("--instruction", type=str, help="Task instruction string")

    args = parser.parse_args()

    if args.validate:
        if not args.plugin:
            print("Error: --plugin path is required for validation.")
            sys.exit(1)
        success = validate_maf_plugin(Path(args.plugin))
        sys.exit(0 if success else 1)
    
    if args.skill:
        sim_path = Path(args.skill)
        in_file = Path(args.input) if args.input else None
        inst = args.instruction if args.instruction else "No instruction provided"
        simulate_maf_run(sim_path, in_file, inst)
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()
