"""
[SKILL_ROOT]/scripts/analyze_tracking_status.py
================================================

Purpose:
    Generates a summary report of AI Analysis progress from the tracking file.
    Shows analyzed vs pending forms for project management dashboards.

Input:
    - [PROJECT_ROOT]/legacy-system/reference-data/ai_analysis_tracking.json

Usage:
    python [SKILL_ROOT]/scripts/analyze_tracking_status.py
"""
import json
import os
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
TRACKING_FILE = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'ai_analysis_tracking.json'

def analyze_status():
    if not TRACKING_FILE.exists():
        print(f"Error: Tracking file not found at {TRACKING_FILE}")
        return

    try:
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    forms = data.get('forms', {})
    
    total = len(forms)
    analyzed_count = 0
    pending_list = []

    print(f"\n{'='*60}")
    print(f"AI Analysis Tracking Summary")
    print(f"{'='*60}")

    for form_id, info in forms.items():
        status = info.get('aiAnalysisStatus', 'pending').lower()
        if status in ['analyzed', 'completed']:
            analyzed_count += 1
        else:
            pending_list.append({
                'id': form_id, 
                'name': info.get('objectName', 'Unknown'),
                'status': status
            })

    print(f"Total Forms Tracked: {total}")
    print(f"✅ Fully Analyzed:    {analyzed_count}")
    print(f"⚠️  Pending/Review:    {len(pending_list)}")
    print(f"{'='*60}\n")
    
    if pending_list:
        print("Forms Requiring Deep Dive (Pending/Needs Review):")
        print(f"{'-'*80}")
        print(f"{'Form ID':<12} | {'Status':<15} | {'Description'}")
        print(f"{'-'*80}")
        for item in pending_list:
            print(f"{item['id']:<12} | {item['status']:<15} | {item['name']}")
        print(f"{'-'*80}\n")

if __name__ == "__main__":
    analyze_status()
