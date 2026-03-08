#!/usr/bin/env python3
import os
import re
from pathlib import Path

def resolve_project_root() -> Path:
    return Path.cwd()

def fix_python_files(root: Path):
    plugins_dir = root / "plugins"
    fixes = 0
    files_fixed = 0
    
    # regexes to target specific violations identified in output
    replacements = [
        # Match python3 plugins/... execution commands in markdown examples
        (r'(["\'`]?)python3\s+plugins/[a-zA-Z0-9_\-]+/(?:skills/[a-zA-Z0-9_\-]+/)?(scripts/[a-zA-Z0-9_\-\.]+)(["\'`]?)', r'\1python3 ./\2\3'),
        # Match config/tool paths inside strings in python like "plugins/tool_inventory.json"
        (r'ROOT / "plugins/tool_inventory.json"', r'ROOT / "tool_inventory.json"'),
        (r'Path\("plugins/tool_inventory.json"\)', r'Path("tool_inventory.json")'),
        (r'["\']plugins/tool_inventory.json["\']', r'"tool_inventory.json"'),
        # Match specific comments 
        (r'# File is at: plugins/[a-zA-Z0-9_\-]+/skills/[a-zA-Z0-9_\-]+/([a-zA-Z0-9_\-\./]+)', r'# File is at: ./\1'),
        (r'# plugins/[a-zA-Z0-9_\-]+/skills/[a-zA-Z0-9_\-]+/([a-zA-Z0-9_\-\./]+) ->', r'# ./\1 ->'),
    ]

    for ext in ("*.py", "*.md", "*.mmd"):
        for file_path in plugins_dir.rglob(ext):
            if file_path.name in ["validate_local_links.py", "auto_fix_local_links.py", "fix_script_paths.py", "fix_script_paths_v2.py", "fix_symlinks_all.py"]:
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8")
                new_content = content
                
                for pattern, repl in replacements:
                    new_content = re.sub(pattern, repl, new_content)

                if new_content != content:
                    file_path.write_text(new_content, encoding="utf-8")
                    files_fixed += 1
                    fixes += 1
                    
            except UnicodeDecodeError:
                pass

    print(f"Fixed {files_fixed} files.")

if __name__ == "__main__":
    fix_python_files(resolve_project_root())
