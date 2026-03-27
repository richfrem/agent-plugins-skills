"""
[SKILL_ROOT]/scripts/update_analysis_tracking.py
=================================================

Purpose:
    Updates the ai_analysis_tracking.json with documentation and analysis status.
    Called by analysis tools to record progress.

Input:
    - Form ID and status parameters

Output:
    - [PROJECT_ROOT]/legacy-system/reference-data/ai_analysis_tracking.json

Usage:
    python [SKILL_ROOT]/scripts/update_analysis_tracking.py FORM0000
"""
from pathlib import Path
import json
import argparse
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
TRACKING_FILE = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'ai_analysis_tracking.json'

import re

def update_tracking(form_id, doc_status=None, ai_status=None, notes=None):
    if not TRACKING_FILE.exists():
        print(f"Error: Tracking file not found at {TRACKING_FILE}")
        return

    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    if 'forms' not in data:
        data['forms'] = {}

    timestamp = datetime.utcnow().isoformat() + 'Z'
    form_id = form_id.upper()
    
    found = False
    
    # Check all sections
    for section in ['forms', 'libraries', 'menus']:
        if section not in data:
            continue
            
        if form_id in data[section]:
            print(f"Updating existing entry for {form_id} in {section}")
            entry = data[section][form_id]
            if doc_status: entry['documentationStatus'] = doc_status
            if ai_status: entry['aiAnalysisStatus'] = ai_status
            entry['lastAnalyzedByAI'] = timestamp
            if notes: entry['notes'] = notes
            found = True
            break
            
    # If not found but force create? The original logic was strict.
    # To support new Menus/Libraries we should probably create if not exists, but strictly under 'menus' if type known?
    # For now, stick to update-only logic to avoid polluting, but fallback to creating in 'menus' if name implies?
    # Let's just fix the lookup logic first.
    
    if found:
        with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully updated {form_id} in tracking file.")
    else:
        # If not found in any section, and it looks like a menu...
        if form_id.endswith("MENU") or form_id == "EXAMPLE_LIB2":
             print(f"Creating new entry for {form_id} in menus")
             if 'menus' not in data: data['menus'] = {}
             data['menus'][form_id] = {
                 "objectName": f"{form_id} Menu",
                 "documentationStatus": doc_status or "Enriched",
                 "sourceAvailable": True,
                 "lastAnalyzedByAI": timestamp,
                 "aiAnalysisStatus": ai_status or "analyzed",
                 "notes": notes or ""
             }
             with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
             print(f"Successfully created {form_id} in menus section.")
        else:
             print(f"ERROR: ID {form_id} not found in forms/libraries/menus. No record was updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update AI Analysis Tracking JSON.')
    parser.add_argument('form_id', help='The Form ID to update (e.g., FORM0000)')
    parser.add_argument('--doc-status', default='Enriched', help='Documentation status (default: Enriched)')
    parser.add_argument('--ai-status', default='analyzed', help='AI Analysis status (default: analyzed)')
    parser.add_argument('--notes', help='Analysis notes')

    args = parser.parse_args()
    update_tracking(args.form_id, args.doc_status, args.ai_status, args.notes)

