
import shutil
import os
from pathlib import Path

def clean_dir(target_dir):
    path = Path.cwd() / target_dir
    if not path.exists():
        print(f"Skipping {target_dir} (not found)")
        return

    print(f"Cleaning {target_dir}...")
    for item in path.iterdir():
        if item.is_dir():
            print(f"  - Removing directory: {item.name}")
            shutil.rmtree(item)

if __name__ == "__main__":
    clean_dir(".claude/commands")
    clean_dir(".gemini/commands")
    clean_dir(".github/prompts") 
