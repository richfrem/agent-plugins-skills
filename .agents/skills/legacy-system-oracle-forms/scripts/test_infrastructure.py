"""
plugins/legacy-system-oracle-forms/scripts/test_infrastructure.py

Purpose: Verifies the Hybrid Discovery Tooling (Method A/B/C) on sample artifacts.
Layer: Shared/Utilities
Used by: Continuous Integration, developers
"""
import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from tools.investigate.utils.path_resolver import resolve_path

# Setup Paths
MINERS_DIR = Path(resolve_path("tools/investigate/miners"))
SEARCH_DIR = Path(resolve_path("tools/investigate/search"))
OUTPUT_DIR = Path(resolve_path("legacy-system/analysis-outputs/hybrid-discovery/test-run"))

def run_test(name, command_args, output_file_name=None):
    print(f"--- Testing {name} ---")
    
    cmd = [sys.executable] + command_args
    if output_file_name:
        out_path = os.path.join(OUTPUT_DIR, output_file_name)
        cmd.extend(["--out", out_path])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        if result.returncode != 0:
            print(f"FAILED: {result.stderr}")
            return False, None
        else:
            print("SUCCESS")
            # print(result.stdout[:200] + "...") # Preview
            if output_file_name:
                return True, os.path.join(OUTPUT_DIR, output_file_name)
            return True, result.stdout
            
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def verify_json(file_path, key_checks):
    """Checks if JSON file exists and contains specific keys/values."""
    if not os.path.exists(file_path):
        print(f"Verification FAILED: File not found {file_path}")
        return False
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        print(f"Verifying {os.path.basename(file_path)}...")
        
        # Helper recursive check? Simple check for now.
        # Check if list is not empty
        empty = True
        if isinstance(data, dict):
            for k, v in data.items():
                if v and len(v) > 0: 
                    empty = False
                    break
        elif isinstance(data, list) and len(data) > 0:
             empty = False
             
        if empty:
            print("WARNING: Output JSON is empty or has no rules.")
            
        # Specific Checks
        for key, expected_val in key_checks.items():
            # Simplistic check: If key exists in string dump or top level
            # For lists of dicts, it's harder. We'll do string search on dump for simplicity
            dump = json.dumps(data)
            if expected_val in dump:
                print(f"  [OK] Found '{expected_val}' relative to '{key}'")
            else:
                print(f"  [FAIL] Missing '{expected_val}' relative to '{key}'")
                
        return True
    except Exception as e:
        print(f"Verification Error: {e}")
        return False

def main():
    print(f"Starting Infrastructure Test...")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    # ensure clean start
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
    
    overall_success = True

    # 1. XML Miner (Form)
    ok, outfile = run_test("XML Miner", 
        [str(MINERS_DIR / "xml_miner.py"), "--target", "JCSE0086"], 
        "jcse0086_rules.json")
    if ok: verify_json(outfile, {"Item": "REQUIRED", "Block": "WHERE_CLAUSE"}) # Generic terms to look for
    
    # 2. Reachability (Form)
    ok, stdout = run_test("Reachability", 
        [str(SEARCH_DIR / "reachability.py"), "--target", "JCSE0086"])
    if ok:
        if "score" in stdout: print("  [OK] Reachability Score Calculated")
    
    # 3. LDS Scorer (Form)
    ok, outfile = run_test("LDS Scorer", 
        [str(SEARCH_DIR / "lds_scorer.py"), "--target", "JCSE0086"], 
        "jcse0086_lds.json")
    if ok: verify_json(outfile, {"LDS_Score": "Metric"})
    
    # 4. PLL Miner (Full Scan)
    ok, outfile = run_test("PLL Miner", 
        [str(MINERS_DIR / "pll_miner.py")], 
        "pll_rules.json")
    if ok: verify_json(outfile, {"AGLIB": "AGLIB", "PublicAPI": "PublicAPI"})
    
    # 5. DB Miner (Full Scan)
    ok, outfile = run_test("DB Miner", 
        [str(MINERS_DIR / "db_miner.py")], 
        "db_rules.json")
    if ok: verify_json(outfile, {"ValidationRules": "ValidationRules"})

    print("\nTest Complete.")

if __name__ == "__main__":
    main()
