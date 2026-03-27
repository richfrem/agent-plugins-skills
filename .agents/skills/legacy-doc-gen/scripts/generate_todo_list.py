"""
[SKILL_ROOT]/scripts/generate_todo_list.py
===========================================

Purpose:
    Creates a prioritized TODO list of forms pending AI analysis.
    Bubbles up Critical and High priority items based on workflow usage.

Output:
    - [PROJECT_ROOT]/TODO_PENDING_ANALYSIS.md

Usage:
    python [SKILL_ROOT]/scripts/generate_todo_list.py
"""
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
BASE_DIR = PROJECT_ROOT

TRACKING_FILE = BASE_DIR / 'legacy-system' / 'reference-data' / 'ai_analysis_tracking.json'
OUTPUT_FILE = BASE_DIR / 'TODO_PENDING_ANALYSIS.md'

WORKFLOW_FILE = BASE_DIR / 'legacy-system' / 'business-workflows' / 'BC_Criminal_Justice_Workflow_Summary.md'
APPS_DIR = BASE_DIR / 'legacy-system' / 'applications'

def extract_form_ids(text):
    return set(re.findall(r'\b[A-Z]{3,4}[EMR][0-9]{4}\b', text))

def get_priority_forms():
    workflow_forms = set()
    app_forms = set()

    # Scan Workflow
    if WORKFLOW_FILE.exists():
        content = WORKFLOW_FILE.read_text(encoding='utf-8')
        workflow_forms = extract_form_ids(content)
    
    # Scan Applications
    if APPS_DIR.exists():
        for md_file in APPS_DIR.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            app_forms.update(extract_form_ids(content))

    return workflow_forms, app_forms

def generate_todo():
    if not TRACKING_FILE.exists():
        return

    workflow_ids, app_ids = get_priority_forms()

    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    forms = data.get('forms', {})
    pending = []

    for form_id, info in forms.items():
        status = info.get('aiAnalysisStatus', 'pending').lower()
        if status not in ['analyzed', 'completed']:
            
            # Determine Priority
            is_workflow = form_id in workflow_ids
            is_app_core = form_id in app_ids
            
            priority_score = 0
            priority_label = "Standard"
            
            if is_workflow and is_app_core:
                priority_score = 3
                priority_label = "🔥 CRITICAL (Workflow + App)"
            elif is_workflow:
                priority_score = 2
                priority_label = "⚡ HIGH (Workflow Step)"
            elif is_app_core:
                priority_score = 2
                priority_label = "⭐ HIGH (App Core)"
            
            pending.append({
                'id': form_id,
                'name': info.get('objectName', 'Unknown'),
                'app': form_id[:3],
                'priority_score': priority_score,
                'priority_label': priority_label
            })

    # Sort by Priority (Desc), then App, then ID
    pending.sort(key=lambda x: (-x['priority_score'], x['app'], x['id']))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Pending AI Analysis To-Do List (Prioritized)\n\n")
        f.write(f"**Total Pending:** {len(pending)}\n\n")
        f.write("Forms found in the **Criminal Justice Workflow** or **Application Overviews** are bubbled to the top.\n\n")
    
        current_priority = -1
        
        for item in pending:
            if item['priority_score'] != current_priority:
                current_priority = item['priority_score']
                f.write(f"\n### {item['priority_label']}\n")
                f.write(f"| Form ID | Application | Form Name |\n")
                f.write(f"| :--- | :--- | :--- |\n")
            
            f.write(f"| **{item['id']}** | {item['app']} | {item['name']} |\n")

    print(f"✅ Generated {OUTPUT_FILE} with {len(pending)} items (Prioritized).")

if __name__ == "__main__":
    generate_todo()
