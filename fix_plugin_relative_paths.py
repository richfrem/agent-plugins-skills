import os
import re
from pathlib import Path

def fix_paths(root_dir: Path):
    plugins_dir = root_dir / "plugins"
    if not plugins_dir.exists():
        print(f"Error: {plugins_dir} not found.")
        return

    # Pattern 1: python3 plugins/A/scripts/foo.py -> python3 ./scripts/foo.py (if inside plugins/A)
    # Pattern 2: [label](plugins/A/skills/S/assets/img.png) -> [label](./assets/img.png) (if inside plugins/A/skills/S)
    
    total_files = 0
    total_fixes = 0

    for md_file in plugins_dir.rglob("*.md"):
        # Identify the Home Plugin
        try:
            rel_path = md_file.relative_to(plugins_dir)
            parts = rel_path.parts
        except ValueError:
            continue
            
        if not parts:
            continue
        home_plugin = parts[0]
        
        # Identify if we are inside a specific skill
        home_skill = None
        if len(parts) >= 3 and parts[1] == "skills":
            home_skill = parts[2]

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
            
        original_content = content
        
        # Rule 1: Self-referential script paths
        # Match plugins/<HOME_PLUGIN>/scripts/
        # We use a broad match to catch various usage styles (bash, markdown links, etc)
        script_pattern = rf'plugins/{home_plugin}/scripts/'
        content = content.replace(script_pattern, "./scripts/")
        
        # Rule 2: Self-referential skill assets
        if home_skill:
            asset_pattern = rf'plugins/{home_plugin}/skills/{home_skill}/assets/'
            content = content.replace(asset_pattern, "./assets/")
        
        if content != original_content:
            md_file.write_text(content, encoding="utf-8")
            print(f"Fixed: {md_file.relative_to(root_dir)}")
            total_files += 1

    print(f"\nPhase 1 Complete: {total_files} files updated.")

if __name__ == "__main__":
    # Auto-resolve root from script location
    root = Path(__file__).resolve().parent
    fix_paths(root)
