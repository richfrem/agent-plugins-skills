#!/usr/bin/env python3
"""
bundle.py
=====================================
Purpose: Reads a JSON manifest file and concatenates contents into a single Markdown artifact.
[v2.1] Adds manifest 'excludes', 5MB large-file safety, cumulative tokens, and expanded lang map.
"""

import sys
import json
import argparse
import fnmatch
from pathlib import Path
from datetime import datetime

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB safety limit

def load_gitignore_patterns(project_root: Path) -> list:
    patterns = ['.git', '__pycache__', 'node_modules', '.env'] 
    gi_path = project_root / '.gitignore'
    if gi_path.exists():
        try:
            with open(gi_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception:
            pass
    return patterns

def is_ignored(file_path: Path, project_root: Path, patterns: list) -> bool:
    try:
        rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
    except ValueError:
        return False

    for pattern in patterns:
        clean_pattern = pattern.strip('/')
        if (fnmatch.fnmatch(rel_path, clean_pattern) or 
            fnmatch.fnmatch(rel_path, f"{clean_pattern}/*") or 
            fnmatch.fnmatch(rel_path, f"*/{clean_pattern}/*") or 
            fnmatch.fnmatch(rel_path, f"*/{clean_pattern}")):
            return True
    return False

def bundle_files(manifest_path: Path, output_path: Path) -> None:
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest '{manifest_path}': {e}")
        sys.exit(1)

    title = manifest.get('title', 'Context Bundle')
    description = manifest.get('description', '')
    files = manifest.get('files', [])
    
    # Merge .gitignore with manifest-specific excludes
    project_root = Path.cwd()
    ignore_patterns = load_gitignore_patterns(project_root)
    ignore_patterns.extend(manifest.get('excludes', []))

    resolved_files = []
    total_tokens = 0
    valid_file_count = 0
    missing_files = []

    print("🔍 Resolving files and calculating token budgets...")

    for entry in files:
        path_str = entry.get('path', '')
        note = entry.get('note', '')
        actual_path = project_root / path_str
        
        if actual_path.is_dir():
            for file_path in actual_path.rglob('*'):
                if file_path.is_file() and not is_ignored(file_path, project_root, ignore_patterns):
                    rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
                    
                    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                        resolved_files.append({'path': rel_path, 'note': note, 'too_large': True})
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as peek:
                            content = peek.read()
                            tokens = len(content) // 4
                            total_tokens += tokens
                            
                        resolved_files.append({
                            'path': rel_path,
                            'note': f"{note} (from {path_str})" if note else f"from {path_str}",
                            'tokens': tokens,
                            'content': content
                        })
                        valid_file_count += 1
                    except UnicodeDecodeError:
                        resolved_files.append({'path': rel_path, 'note': note, 'binary': True})
        else:
            if not actual_path.exists():
                missing_files.append(path_str)
                resolved_files.append({'path': path_str, 'note': note, 'missing': True})
            elif not is_ignored(actual_path, project_root, ignore_patterns):
                if actual_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    resolved_files.append({'path': path_str, 'note': note, 'too_large': True})
                    continue
                    
                try:
                    with open(actual_path, 'r', encoding='utf-8') as peek:
                        content = peek.read()
                        tokens = len(content) // 4
                        total_tokens += tokens
                        
                    resolved_files.append({
                        'path': path_str,
                        'note': note,
                        'tokens': tokens,
                        'content': content
                    })
                    valid_file_count += 1
                except UnicodeDecodeError:
                    resolved_files.append({'path': path_str, 'note': note, 'binary': True})

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"# {title}\n")
        out.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if description:
            out.write(f"{description}\n\n")

        out.write("### 📊 Bundle Metadata\n")
        out.write(f"- **Total Files:** {valid_file_count}\n")
        out.write(f"- **Estimated Tokens:** ~{total_tokens:,}\n")
        if total_tokens > 100000:
            out.write("- ⚠️ *Warning: This bundle is extremely large. Ensure your target LLM supports 100k+ context windows.*\n")
        out.write("\n---\n\n")

        out.write("## 📑 Index\n")
        cumulative_tokens = 0
        for idx, entry in enumerate(resolved_files, 1):
            path_str = entry.get('path', '')
            note = entry.get('note', '')
            
            if entry.get('missing'):
                out.write(f"{idx}. ❌ `{path_str}` - *FILE NOT FOUND*\n")
            elif entry.get('binary'):
                out.write(f"{idx}. 🗜️ `{path_str}` - *[Binary File Skipped]*\n")
            elif entry.get('too_large'):
                out.write(f"{idx}. ⚠️ `{path_str}` - *[Skipped: Exceeds 5MB Limit]*\n")
            else:
                tokens = entry.get('tokens', 0)
                cumulative_tokens += tokens
                out.write(f"{idx}. `{path_str}` ({tokens:,} tokens | {cumulative_tokens:,} total)")
                if note:
                    out.write(f" - {note}")
                out.write("\n")

        out.write("\n---\n\n")

        # Map common extensions to markdown fence languages
        lang_map = {
            'md': 'markdown', 'mdx': 'markdown', 'py': 'python', 'json': 'json',
            'ts': 'typescript', 'tsx': 'typescript', 'js': 'javascript', 'jsx': 'javascript',
            'yml': 'yaml', 'yaml': 'yaml', 'toml': 'toml', 'sql': 'sql', 'sh': 'bash',
            'bash': 'bash', 'html': 'html', 'css': 'css', 'go': 'go', 'rs': 'rust',
            'cpp': 'cpp', 'c': 'c', 'h': 'c', 'java': 'java'
        }

        for entry in resolved_files:
            if entry.get('missing') or entry.get('binary') or entry.get('too_large'):
                continue
                
            path_str = entry.get('path', '')
            note = entry.get('note', '')
            content = entry.get('content', '')
            
            out.write(f"## File: `{path_str}`\n")
            if note:
                out.write(f"> Note: {note}\n\n")

            ext = Path(path_str).suffix.lower().strip('.')
            lang = lang_map.get(ext, ext if ext else 'text')

            if lang == 'markdown':
                out.write("````markdown\n")
                out.write(content if content.endswith('\n') else content + '\n')
                out.write("````\n\n")
            else:
                out.write(f"```{lang}\n")
                out.write(content if content.endswith('\n') else content + '\n')
                out.write("```\n\n")
            
            out.write("---\n\n")

    print(f"✅ Context successfully bundled into -> {output_path}")
    print(f"📊 Processed {valid_file_count} files (~{total_tokens:,} tokens).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a markdown context bundle from a JSON manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to the JSON manifest.")
    parser.add_argument("--bundle", required=True, type=Path, help="Output path for the Markdown file.")
    args = parser.parse_args()
    bundle_files(args.manifest, args.bundle)