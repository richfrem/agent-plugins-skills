#!/usr/bin/env python3
"""
Batch Project Form Dependency Analyzer
=====================================

Purpose:
    Iterates through all Project Form objects in the collection file and runs
    the dependency_utility.py script for each form to generate dependency graphs.

Input:
    - FormAndReportCollection.ts (Form/Report collection file)
    - dependency_utility.py (Dependency graph generator)

Output:
    - Dependency graph files for each Project Form (via dependency_utility.py)

Key Functions:
    - Extracts FORM object IDs from collection using regex
    - Invokes dependency_utility.py with --NodeToQuery and --levels 3 for each form

Usage:
    python run_all_form_dependencies.py

Related:
    - dependency_utility.py: Single-form dependency graph generator
    - GenerateFormDependencyGraph.py: Alternative visualization tool
"""

import subprocess
import re
import os
import sys
from pathlib import Path

# Setup Path Resolution
current_dir = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in current_dir.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

project_root = _find_project_root()
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tools.investigate.utils.path_resolver import resolve_path

# Path to the FormAndReportCollection.ts file
collection_path = resolve_path("legacy-system/reference-data/collections/FormAndReportCollection.ts")

# Path to the dependency utility script
script_path = resolve_path("tools/investigate/search/dependency_utility.py")

# Output directory (optional, script writes to default location)

# Extract all Project FORM object IDs from the collection file
form_ids = []
with open(collection_path, encoding='utf-8') as f:
    for line in f:
        match = re.search(r"OBJECT_ID:\s*'([A-Z0-9]+)'[ ,].*OBJECT_TYPE:\s*'FORM'", line)
        if match:
            form_ids.append(match.group(1))

print(f"Found {len(form_ids)} Project forms.")

# Run the dependency utility for each form
for form_id in form_ids:
    print(f"\n=== Processing {form_id} ===")
    cmd = [
        'python',
        script_path,
        '--NodeToQuery', form_id,
        '--levels', '3'
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {form_id}: {e}")
