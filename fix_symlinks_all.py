#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def convert_symlinks_to_hardlinks(root_dir: Path):
    plugins_dir = root_dir / "plugins"
    for skill_dir in plugins_dir.rglob("skills/*"):
        if not skill_dir.is_dir():
            continue
            
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.exists():
            continue
            
        for file in scripts_dir.iterdir():
            if file.is_symlink():
                target = os.readlink(file)
                if file.suffix == ".py" or file.suffix == ".sh":
                    target_path = (scripts_dir / target).resolve()
                    if target_path.exists():
                        print(f"Converting {file.relative_to(root_dir)} to hardlink -> {target_path.relative_to(root_dir)}")
                        os.unlink(file)
                        os.link(target_path, file)

if __name__ == "__main__":
    current = Path.cwd()
    convert_symlinks_to_hardlinks(current)
