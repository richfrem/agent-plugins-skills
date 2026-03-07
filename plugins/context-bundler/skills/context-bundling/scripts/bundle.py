#!/usr/bin/env python3
"""
Context Bundler Engine

A simple utility that reads a JSON manifest file containing a list of
file paths and notes, and concatenates their contents into a single
Markdown artifact suitable for LLM context ingestion.

Creates technical bundles of code, design, and documentation for external 
review or context sharing. Use when you need to package multiple project 
files into a single Markdown file while preserving folder hierarchy and 
providing contextual notes for each file.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def generate_bundle(manifest_path: Path, output_path: Path) -> None:
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

    # Always write from the project root (where the script is called from ideally)
    project_root = Path.cwd()

    resolved_files = []
    for entry in files:
        path_str = entry.get('path', '')
        note = entry.get('note', '')
        actual_path = project_root / path_str
        
        if actual_path.is_dir():
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

    with open(output_path, 'w', encoding='utf-8') as out:
        # 1. Header
        out.write(f"# {title}\n")
        out.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if description:
            out.write(f"{description}\n\n")

        # 2. Table of Contents / Index
        out.write("## Index\n")
        missing_files = []

        for idx, entry in enumerate(resolved_files, 1):
            path_str = entry.get('path', '')
            note = entry.get('note', '')
            
            # Use relative paths for display if under cwd
            display_path = path_str
            
            out.write(f"{idx}. `{display_path}`")
            if note:
                out.write(f" - {note}")
            out.write("\n")
            
            # Check existence
            actual_path = project_root / path_str
            if not actual_path.exists():
                missing_files.append(path_str)

        out.write("\n---\n\n")
        
        if missing_files:
            print(f"Warning: {len(missing_files)} files listed in manifest were not found.")

        # 3. File Contents
        for entry in resolved_files:
            path_str = entry.get('path', '')
            note = entry.get('note', '')
            actual_path = project_root / path_str

            out.write(f"## File: `{path_str}`\n")
            if note:
                out.write(f"> Note: {note}\n\n")
            
            if not actual_path.exists():
                out.write("> [!WARNING] File not found or inaccessible at generation time.\n\n")
                out.write("---\n\n")
                continue

            try:
                # Basic language inference for markdown block
                ext = actual_path.suffix.lower().strip('.')
                lang = 'markdown' if ext in ['md', 'mdx'] else \
                       'python' if ext == 'py' else \
                       'json' if ext == 'json' else \
                       'typescript' if ext in ['ts', 'tsx'] else \
                       'javascript' if ext in ['js', 'jsx'] else ext

                with open(actual_path, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()
                    
                    if lang == 'markdown':
                         # Don't enclose markdown within markdown if possible, just write it
                         # Or use 4 backticks to enclose 3 backticks
                         out.write("````markdown\n")
                         out.write(content)
                         if not content.endswith('\n'):
                             out.write('\n')
                         out.write("````\n\n")
                    else:
                        out.write(f"```{lang}\n")
                        out.write(content)
                        if not content.endswith('\n'):
                            out.write('\n')
                        out.write("```\n\n")
            except Exception as e:
                 out.write(f"> [!ERROR] Could not read file contents: {e}\n\n")
            
            out.write("---\n\n")

    print(f"✅ Context successfully bundled into -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a markdown context bundle from a JSON manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to the JSON file manifest.")
    parser.add_argument("--bundle", required=True, type=Path, help="Output path for the bundled Markdown file.")
    
    args = parser.parse_args()
    
    generate_bundle(args.manifest, args.bundle)

if __name__ == "__main__":
    main()
