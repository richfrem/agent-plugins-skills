#!/usr/bin/env python3
"""
capture_role_profile.py
=======================
Purpose: Captures search tool output (Menus, Buttons, Reports) for a specific Role
         directly into JSON files, bypassing shell stdout truncation issues.

Usage:
    python plugins/legacy-system-roles/scripts/capture_role_profile.py "ROLE_NAME"
"""
import subprocess
import json
import sys
import os
import argparse

def capture(tool_name, role, output_file, args=[]):
    # Construct absolute path to tool to be safe
    tool_path = os.path.join("tools", "investigate", "search", tool_name)
    
    cmd = [sys.executable, tool_path, role, "--json"] + args
    print(f"Running {' '.join(cmd)}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"Error running {tool_name}: {result.stderr}")
            return
        
        # Validating JSON
        try:
            data = json.loads(result.stdout)
            # Ensure output dir exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Success! {len(data)} items saved to {output_file}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON from {tool_name}: {e}")
            print(f"Snippet: {result.stdout[:200]}...")
            
    except Exception as e:
        print(f"Execution failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Capture Role Profile Data")
    parser.add_argument("role", help="Target Role Name")
    args = parser.parse_args()
    
    clean_role = args.role.replace(" ", "_").upper()
    
    print(f"--- Capturing Profile for {args.role} ---")
    
    # 1. Menus (MIP only per policy)
    capture("search_menu_rules.py", args.role, f"temp/profile_{clean_role}_menus.json", args=["--type", "MIP"])
    
    # 2. Buttons
    capture("search_button_rules.py", args.role, f"temp/profile_{clean_role}_buttons.json")
    
    # 3. Reports
    capture("search_report_rules.py", args.role, f"temp/profile_{clean_role}_reports.json", args=["--type", "role"])

if __name__ == "__main__":
    main()
