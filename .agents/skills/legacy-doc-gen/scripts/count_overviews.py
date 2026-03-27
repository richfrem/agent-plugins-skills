"""
[SKILL_ROOT]/scripts/count_overviews.py

Purpose: Counts total Overview markdown files in the forms directory.
Layer: Investigate / Utils
Used by: Reporting, Dashboard

Usage:
    python [SKILL_ROOT]/scripts/count_overviews.py
"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()

path = PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'forms'
try:
    files = list(path.glob('*.md'))
    print(f"Total Overview Files: {len(files)}")
    print(f"Sample files: {[f.name for f in files[:5]]}")
except Exception as e:
    print(f"Error: {e}")
