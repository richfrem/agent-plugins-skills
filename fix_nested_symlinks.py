#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def resolve_project_root() -> Path:
    return Path.cwd()

def fix_nested_symlinks(root: Path):
    plugins_dir = root / "plugins"
    fixed_count = 0
    
    # We are looking for structure like:
    # plugins/rlm-factory/skills/rlm-curator/resources (dir)
    # └── resources -> ../../resources (symlink inside dir)
    #
    # It SHOULD be:
    # plugins/rlm-factory/skills/rlm-curator/resources -> ../../resources
    
    for skill_dir in plugins_dir.rglob("skills/*"):
        if not skill_dir.is_dir():
            continue
            
        for folder_name in ["resources", "references"]:
            target_dir = skill_dir / folder_name
            
            if target_dir.is_dir() and not target_dir.is_symlink():
                # check if it contains a symlink to itself
                nested_symlink = target_dir / folder_name
                if nested_symlink.is_symlink():
                    print(f"Fixing nested symlink in {skill_dir.relative_to(root)}")
                    
                    # 1. read where it points
                    target = os.readlink(nested_symlink)
                    
                    # 2. remove the nested symlink
                    nested_symlink.unlink()
                    
                    # 3. remove the dir if it's now empty
                    if not any(target_dir.iterdir()):
                        target_dir.rmdir()
                        
                        # 4. create the correct symlink at the target_dir level
                        # We need to drop one level of ../ from target since we moved up one level
                        # target is usually "../../resources". Now we want "../../resources" (Wait, 
                        # if we moved up from resources to skill_dir, the distance is the same.
                        # Wait, from skill_dir/resources/resources it's ../../resources (root)
                        # So from skill_dir/resources it's just ../../resources.
                        # Actually from skill_dir, the root resources is ../../resources
                        os.symlink(target, target_dir)
                        fixed_count += 1
                    else:
                        print(f"  Cannot flatten {target_dir.relative_to(root)} - contains other files")

    print(f"Fixed {fixed_count} nested symlinks.")

if __name__ == "__main__":
    fix_nested_symlinks(resolve_project_root())
