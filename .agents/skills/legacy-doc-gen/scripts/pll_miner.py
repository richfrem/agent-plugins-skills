#!/usr/bin/env python3
"""
pll_miner.py (CLI)
=====================================

Purpose:
    Extracts API, Globals, Calls from Library dumps.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-oracle-forms/scripts/pll_miner.py --help
    python plugins/legacy-system-oracle-forms/scripts/pll_miner.py --target AGLIB --json
    python plugins/legacy-system-oracle-forms/scripts/pll_miner.py --search "INSERT_ACLO" --json
    python plugins/legacy-system-oracle-forms/scripts/pll_miner.py --target "legacy/pll/EXAMPLE_LIB.txt"  # Analyze file path
    python plugins/legacy-system-oracle-forms/scripts/pll_miner.py --target EXAMPLE_LIB --out rules.json  # Save analysis to JSON

Supported Object Types:
    - Generic

CLI Arguments:
    --target        : Specific PLL ID (e.g., AGLIB) or file path to analyze
    --search        : Keyword to search across all PLLs
    --out           : Path to save JSON output
    --json          : Output raw JSON to stdout (suppress logs)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import json
import argparse
import glob
from typing import Dict, List, Any, Optional
import sys

# Ensure tools module can be imported
sys.path.append(os.getcwd())

class PllMiner:
    """
    Mines PL/SQL Library (PLL) text dumps for business rules and dependencies.
    """
    def __init__(self):
        self.repo_root = self.get_project_root()
        self.rules: Dict[str, List[Dict[str, Any]]] = {
            "PublicAPI": [],
            "GlobalStateUsage": [],
            "ExternalCalls": [],
            "ValidationLogic": []
        }

    @staticmethod
    def get_project_root() -> str:
        """Determines the absolute path to the Project Root directory."""
        current = os.path.abspath(os.path.dirname(__file__))
        while True:
            if os.path.exists(os.path.join(current, "legacy-system")) or \
               os.path.exists(os.path.join(current, ".agent")):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                return os.getcwd() # Fallback
            current = parent
        self.rules: Dict[str, List[Dict[str, Any]]] = {
            "PublicAPI": [],
            "GlobalStateUsage": [],
            "ExternalCalls": [],
            "ValidationLogic": []
        }

    def scan_plls(self, target: Optional[str] = None, silent: bool = False) -> None:
        """
        Scans PLL files.
        If target is provided, scans only that file.
        Otherwise scans all text files in legacy-system/oracle-forms/pll.
        """
        pll_dir = os.path.join(self.repo_root, "legacy-system", "oracle-forms", "pll")
        
        files_to_scan = []

        if target:
            # Check direct file path provided by user
            if os.path.exists(target) and os.path.isfile(target):
                 files_to_scan.append(target)
            else:
                # Look in pll dir
                t_clean = os.path.basename(target).replace(".txt", "").lower()
                exact = os.path.join(pll_dir, f"{t_clean}.txt")
                if os.path.exists(exact):
                    files_to_scan.append(exact)
                else:
                    print(f"Warning: Could not find PLL file for target '{target}'")
                    return
        else:
            # Full Scan
            if not os.path.exists(pll_dir):
                print(f"Warning: PLL directory not found: {pll_dir}")
                return
            files_to_scan = glob.glob(os.path.join(pll_dir, "*.txt"))

        if not silent:
            print(f"Scanning {len(files_to_scan)} PLL file(s)...")

        for txt_file in files_to_scan:
            pll_name = os.path.basename(txt_file).replace(".txt", "").upper()
            try:
                rel_path = os.path.relpath(txt_file, self.repo_root)
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._analyze_file(pll_name, content, rel_path)
            except Exception as e:
                print(f"Error reading {txt_file}: {e}")

    def _analyze_file(self, pll_name: str, content: str, rel_path: str):
        """Analyzes a single PLL file content."""
        
        # 0. Clean Comments (Critical for accurate regex)
        # Remove /* ... */ multi-line comments
        content_clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove -- ... single-line comments
        content_clean = re.sub(r'--.*$', '', content_clean, flags=re.MULTILINE)

        # Split Spec and Body (roughly)
        # Format usually: PACKAGE x IS ... END; PACKAGE BODY x IS ... END;
        parts = re.split(r'PACKAGE\s+BODY', content_clean, flags=re.IGNORECASE)
        spec = parts[0]
        # body = parts[1] if len(parts) > 1 else ""

        # 1. Public API (from Spec)
        # Matches: PROCEDURE Name (args); or FUNCTION Name (args) RETURN Type;
        # Added strict word boundary and case insensitivity
        # Matches: PROCEDURE Name, FUNCTION Name, PACKAGE Name, TYPE Name
        matches = re.finditer(r'(PROCEDURE|FUNCTION|PACKAGE|TYPE)\s+([a-zA-Z0-9_$]+)', spec, re.IGNORECASE)
        seen_api = set()
        
        # Stopwords still useful as a fallback, but comment stripping should solve 99%
        stopwords = {"IS", "AS", "BEGIN", "END", "DECLARE", "EXCEPTION"}

        for m in matches:
            type_ = m.group(1).title()
            name = m.group(2)
            
            if name.upper() in stopwords:
                continue

            if name not in seen_api:
                self.rules["PublicAPI"].append({
                    "PLL": pll_name,
                    "FilePath": rel_path,
                    "Type": type_,
                    "Name": name
                })
                seen_api.add(name)

        # 2. Global State Usage (from Whole File)
        # Matches: name_in('global.x') or copy('val', 'global.x')
        # We look for 'global.[varname]' literal strings
        global_matches = re.finditer(r"['\"](GLOBAL\.[a-zA-Z0-9_$]+)['\"]", content, re.IGNORECASE)
        seen_globals = set()
        for m in global_matches:
            g_var = m.group(1).upper()
            if g_var not in seen_globals:
                self.rules["GlobalStateUsage"].append({
                    "PLL": pll_name,
                    "FilePath": rel_path,
                    "Variable": g_var,
                    "Usage": "Reference" 
                })
                seen_globals.add(g_var)

        # 3. External Calls (to Forms)
        call_matches = re.finditer(r"(call_form|open_form|new_form)\s*\(\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE)
        for m in call_matches:
            call_type = m.group(1).lower()
            target_form = m.group(2).upper()
            self.rules["ExternalCalls"].append({
                "PLL": pll_name,
                "FilePath": rel_path,
                "CallType": call_type,
                "Target": target_form
            })

        # 4. Validation Logic
        if "RAISE FORM_TRIGGER_FAILURE" in content.upper():
             self.rules["ValidationLogic"].append({
                 "PLL": pll_name,
                 "FilePath": rel_path,
                 "Rule": "Raises Form Trigger Failure (Validation Blocker)",
                 "Count": content.upper().count("RAISE FORM_TRIGGER_FAILURE")
             })

    def search_rules(self, term: str) -> List[str]:
        """Search extracted rules for term."""
        term = term.lower()
        matches = []
        
        for api in self.rules["PublicAPI"]:
            if term in api["Name"].lower():
                matches.append(f"PublicAPI:{api['Name']}")
                
        for call in self.rules["ExternalCalls"]:
            if term in call["Target"].lower():
                matches.append(f"Call:{call['Target']}")
                
        for val in self.rules["ValidationLogic"]:
             if term in val.get("Rule", "").lower():
                  matches.append(f"Validation:{val.get('PLL')}")
                  
        return matches

def main():
    parser = argparse.ArgumentParser(description="Mine Business Rules from PL/SQL Libraries")
    parser.add_argument("--target", help="Specific PLL ID (e.g., EXAMPLE_LIB) or file path to analyze")
    parser.add_argument("--search", help="Keyword to search across all PLLs")
    parser.add_argument("--out", help="Path to save JSON output", default="pll_rules.json")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    args = parser.parse_args()
    
    miner = PllMiner()
    
    if args.target:
        if not args.json:
            print(f"Scanning for target: {args.target}...")
        miner.scan_plls(args.target, silent=args.json)
    elif args.search:
        # Bulk Scan + Search
        pll_dir = os.path.join(miner.repo_root, "legacy-system", "oracle-forms", "pll")
        files = glob.glob(os.path.join(pll_dir, "*.txt"))
        
        if not args.json:
             print(f"Scanning {len(files)} PLLs in {pll_dir} for '{args.search}'...")
             
        unique_paths = set()
        for f in files:
            m = PllMiner()
            m.scan_plls(f, silent=True) # Scan single file, suppress log
            matches = m.search_rules(args.search)
            if matches:
                # Get FilePath from first rule if exists, or calculate
                fp = ""
                # Check PublicAPI
                if m.rules["PublicAPI"]: fp = m.rules["PublicAPI"][0].get("FilePath","")
                elif m.rules["GlobalStateUsage"]: fp = m.rules["GlobalStateUsage"][0].get("FilePath","")
                elif m.rules["ExternalCalls"]: fp = m.rules["ExternalCalls"][0].get("FilePath","")
                
                if not fp:
                     try:
                         fp = os.path.relpath(f, miner.repo_root)
                     except:
                         fp = f
                
                unique_paths.add(fp)

                if not args.json:
                     print(f"[{os.path.basename(f)}] Found {len(matches)} matches")
        
        if args.json:
            print(json.dumps(sorted(list(unique_paths)), indent=2))
        return
    else:
        if not args.json:
            print(f"Scanning Full Library Repository...")
        miner.scan_plls(silent=args.json) # Full scan behavior preserved
        
    output_json = json.dumps(miner.rules, indent=2)

    if args.json:
        print(output_json)
        return
        
    print(f"\nFound {len(miner.rules['PublicAPI'])} Public API Units")
    print(f"Found {len(miner.rules['GlobalStateUsage'])} Global Variable References")
    print(f"Found {len(miner.rules['ExternalCalls'])} External Calls (Forms/Reports)")
    print(f"Found {len(miner.rules['ValidationLogic'])} Validation Rules")
    
    if args.out:
        with open(args.out, 'w') as f:
            f.write(output_json)
        print(f"Saved to {args.out}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()
