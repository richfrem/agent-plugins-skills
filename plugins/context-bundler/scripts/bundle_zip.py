#!/usr/bin/env python3
"""
bundle_zip.py
=====================================

Purpose:
    Reads a JSON manifest file containing a list of file paths and notes, and archives them into a single .zip file.

Layer: Meta-Execution

Usage Examples:
    python3 bundle_zip.py --manifest manifest.json --bundle bundle.zip

Supported Object Types:
    - ZIP bundles (bundle.zip)

CLI Arguments:
    --manifest: Path to the JSON file manifest.
    --bundle: Output path for the bundled .zip file.

Input Files:
    - JSON manifest file.

Output:
    - Bundled .zip file.

Key Functions:
    - generate_zip_bundle()

Script Dependencies:
    None

Consumed by:
    - Context bundler workflow
"""

import sys
import json
import argparse
import zipfile
from pathlib import Path
from datetime import datetime

def generate_zip_bundle(manifest_path: Path, output_path: Path) -> None:
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error loading manifest '{manifest_path}': {e}")
        sys.exit(1)

    title = manifest.get('title', 'Context Bundle')
    description = manifest.get('description', '')
    files = manifest.get('files', [])

    if not files:
        print(f"Warning: Manifest '{manifest_path}' contains no files.")

    # Always write from the project root
    project_root = Path.cwd()

    resolved_files = []
    # Identify explicit files and recursively expand any subdirectories passed to us
    for entry in files:
        path_str = entry.get('path', '')
        note = entry.get('note', '')
        actual_path = project_root / path_str
        
        if actual_path.is_dir():
            print(f"Expanding directory branch: {path_str}")
            for file_path in actual_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    if '__pycache__' in file_path.parts or 'node_modules' in file_path.parts or '.env' in file_path.name:
                        continue
                    try:
                        rel_path = str(file_path.relative_to(project_root))
                    except ValueError:
                        rel_path = str(file_path)
                    resolved_files.append({
                        'path': rel_path,
                        'note': f"{note} (from {path_str})" if note else f"from {path_str}"
                    })
        else:
            resolved_files.append(entry)

    # Begin assembling the "_manifest_notes.md" documentation body
    manifest_doc = [
        f"# {title}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    if description:
        manifest_doc.extend([description, ""])
    
    manifest_doc.extend(["## Index", ""])
    
    missing_files = []
    
    # Check paths and build the index
    for idx, entry in enumerate(resolved_files, 1):
        path_str = entry.get('path', '')
        note = entry.get('note', '')
        
        listing = f"{idx}. `{path_str}`"
        if note:
            listing += f" - {note}"
        manifest_doc.append(listing)
        
        actual_path = project_root / path_str
        if not actual_path.exists():
            missing_files.append(path_str)

    manifest_doc.extend(["", "---", ""])
    
    if missing_files:
        print(f"Warning: {len(missing_files)} files listed in manifest were not found.")
        manifest_doc.append("> [!WARNING] The following files were listed in the manifest but missing from the disk during generation:\n")
        for missing in missing_files:
            manifest_doc.append(f"> - `{missing}`")
        manifest_doc.extend(["", "---", ""])

    # Actually compress everything
    print(f"Archiving files into {output_path}...")
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Archive the payload files
            for entry in resolved_files:
                path_str = entry.get('path', '')
                actual_path = project_root / path_str
                if actual_path.exists():
                    zipf.write(actual_path, arcname=path_str)

            # 2. Finally inject the dynamic manifest documentation
            zipf.writestr('_manifest_notes.md', '\n'.join(manifest_doc))
            
    except Exception as e:
        print(f"Failed to generate ZIP archive: {e}")
        sys.exit(1)

    print(f"✅ Context successfully bundled into -> {output_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a ZIP context bundle from a JSON manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to the JSON file manifest.")
    parser.add_argument("--bundle", required=True, type=Path, help="Output path for the bundled .zip file.")
    
    args = parser.parse_args()
    
    generate_zip_bundle(args.manifest, args.bundle)

if __name__ == "__main__":
    main()
