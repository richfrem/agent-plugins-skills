"""
[SKILL_ROOT]/scripts/summarize_unanalyzed_forms.py
===================================================

Purpose:
    Generates a summary of forms that have not been analyzed by AI, 
    grouped by application.

Output:
    - Console summary output

Usage:
    python [SKILL_ROOT]/scripts/summarize_unanalyzed_forms.py
"""
import json
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
BASE_DIR = PROJECT_ROOT / 'legacy-system'

def summarize():
    tracking_path = BASE_DIR / 'reference-data' / 'ai_analysis_tracking.json'
    inventory_path = BASE_DIR / 'reference-data' / 'inventories' / 'forms_and_reports_inventory.json'

    if not tracking_path.exists() or not inventory_path.exists():
        print("Error: Missing tracking or inventory files.")
        return

    with open(tracking_path, 'r') as f:
        tracking_data = json.load(f)

    with open(inventory_path, 'r') as f:
        inventory_data = json.load(f)

    # Filter unanalyzed forms from tracking
    forms_tracking = tracking_data.get('forms', {})
    unanalyzed_ids = [obj_id for obj_id, info in forms_tracking.items() if info.get('lastAnalyzedByAI') is None]

    # Create inventory lookup for forms only
    inventory_lookup = {item['OBJECT_ID']: item for item in inventory_data if item.get('OBJECT_TYPE') == 'FORM'}

    # Group unanalyzed forms by Application
    summary = {}
    for obj_id in unanalyzed_ids:
        if obj_id in inventory_lookup:
            app = inventory_lookup[obj_id].get('APPLICATION', 'Unknown')
            if app not in summary:
                summary[app] = []
            summary[app].append(obj_id)

    # Print summary
    print("## Unanalyzed Forms Summary")
    print(f"Total Unanalyzed Forms: {len(unanalyzed_ids)}\n")
    
    for app, ids in sorted(summary.items()):
        print(f"### Application: {app} ({len(ids)} forms)")
        # Print a few examples or just the count if there are many
        if len(ids) <= 10:
            print(f"IDs: {', '.join(ids)}")
        else:
            print(f"IDs (first 10): {', '.join(ids[:10])} ...")
        print()

if __name__ == "__main__":
    summarize()
