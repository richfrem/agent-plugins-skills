import os
import re
import json
from pathlib import Path

def analyze_plugins(base_dir):
    plugins_dir = Path(base_dir) / "plugins"
    if not plugins_dir.exists():
        print(f"Error: {plugins_dir} not found.")
        return

    # Load Whitelist
    whitelist = {"global_ignores": {}, "plugin_ignores": {}}
    whitelist_path = Path(__file__).parent / "whitelist.json"
    if whitelist_path.exists():
        try:
            with open(whitelist_path, "r", encoding="utf-8") as f:
                whitelist = json.load(f)
        except Exception as e:
            print(f"Failed to load whitelist.json: {e}")

    global_missing_summary: dict[str, list[tuple[str, list[str]]]] = {}

    # Pre-compute a global index of every physical script in the entire plugin ecosystem
    global_physical_py_files = set()
    for plugin_path in plugins_dir.iterdir():
        if plugin_path.is_dir() and not plugin_path.name.startswith('.'):
            for p in plugin_path.rglob('*.py'):
                if p.is_file():  # Not a symlink, actually exists physically here
                    global_physical_py_files.add(p.name)

    for plugin_path in plugins_dir.iterdir():
        if not plugin_path.is_dir() or plugin_path.name.startswith('.'):
            continue
            
        plugin_name = plugin_path.name
        
        # 1. Find all physical .py files and symlinks in the plugin
        physical_py_files = [] # list of Path
        symlink_py_files = [] # list of Path
        
        for p in plugin_path.rglob('*.py'):
            if p.is_symlink():
                symlink_py_files.append(p)
            elif p.is_file():
                physical_py_files.append(p)
                
        # 2. Map script mentions to skills
        skills_dir = plugin_path / "skills"
        skill_usage = {} # dict mapping script_basename -> set of skill_names
        
        if skills_dir.exists():
            for skill_path in skills_dir.iterdir():
                if not skill_path.is_dir() or skill_path.name.startswith('.'): continue
                skill_name = skill_path.name
                
                # Check all text files in skill for regex *.py
                for p in skill_path.rglob('*'):
                    if p.is_file() and not p.name.startswith('.') and p.suffix in ['.md', '.json', '.py', '.sh', '.txt', '.yaml', '.yml', '.jinja']:
                        try:
                            # Read content carefully
                            content = p.read_text('utf-8')
                            # Match python script names like script.py or script_name.py
                            found_scripts = re.findall(r'[a-zA-Z0-9_-]+\.py', content)
                            for s in found_scripts:
                                # Only add the script to skill usage if it actually exists SOMEWHERE physically in the plugin tree!
                                exists_physically_anywhere = any(p.name == s for p in physical_py_files)
                                if s not in skill_usage: skill_usage[s] = {"skills": set(), "physically_exists": False}
                                skill_usage[s]["skills"].add(skill_name)
                                if exists_physically_anywhere:
                                    skill_usage[s]["physically_exists"] = True
                        except:
                            pass
                
                # If a py file exists in the skill's scripts dir (symlink or physical), consider it used
                for p in skill_path.rglob('*.py'):
                    s = p.name
                    if s not in skill_usage: skill_usage[s] = {"skills": set(), "physically_exists": True}
                    skill_usage[s]["skills"].add(skill_name)
                    skill_usage[s]["physically_exists"] = True
                    
        # Find all unique scripts
        all_unique_scripts = set(skill_usage.keys())
        for p in physical_py_files + symlink_py_files:
            all_unique_scripts.add(p.name)
            
        if not all_unique_scripts:
            continue
            
        print(f"\n{'='*70}")
        print(f"PLUGIN: {plugin_name}")
        print(f"{'='*70}")
        
        for script_name in sorted(all_unique_scripts):
            script_data = skill_usage.get(script_name, {"skills": set(), "physically_exists": False})
            uses = script_data["skills"]
            
            # Physical locations
            physical_locations = [p for p in physical_py_files if p.name == script_name]
            symlink_locations = [p for p in symlink_py_files if p.name == script_name]
            all_locations = physical_locations + symlink_locations
            
            physically_exists = len(all_locations) > 0
            
            root_script_path = plugin_path / "scripts" / script_name
            exists_in_root = False
            for p in all_locations:
                if p == root_script_path:
                    exists_in_root = True
            
            
            if not physically_exists:
                continue
                
            print(f"\nScript: {script_name}")
            print(f"  1. Exists physically in plugin: {'Yes' if physically_exists else 'No'} ({len(all_locations)} location(s))")
            if physically_exists:
                print(f"     -> Exists at pluginroot/scripts: {'Yes' if exists_in_root else 'No'}")
            print(f"  2. Used by skills: {', '.join(sorted(uses)) if uses else 'None'}")
            
            if len(uses) == 1:
                skill_name = list(uses)[0]
                only_in_skill = True
                if len(physical_locations) == 0:
                    only_in_skill = False
                for p in physical_locations:
                    if skill_name not in p.parts:
                        only_in_skill = False
                        break
                print(f"  3. Only used by 1 skill. Physically exists ONLY in that skill ({skill_name})? {'Yes' if only_in_skill else 'No'}")
                if not only_in_skill and physically_exists:
                    print(f"     -> Found in: {[str(p.relative_to(plugin_path)) for p in physical_locations]}")
            elif len(uses) > 1:
                print(f"  4. Used by {len(uses)} skills. Exists in plugin root (scripts/)? {'Yes' if exists_in_root else 'No'}")
                if not exists_in_root and physically_exists:
                     print(f"     -> Physically located in: {[str(p.relative_to(plugin_path)) for p in physical_locations]}")
                if exists_in_root:
                    skills_with_symlink = set()
                    for p in symlink_locations:
                        parts = p.parts
                        if "skills" in parts:
                            idx = parts.index("skills")
                            if idx + 1 < len(parts):
                                skills_with_symlink.add(parts[idx + 1])
                                
                    all_have_symlink = uses.issubset(skills_with_symlink)
                    missing = uses - skills_with_symlink
                    
                    if all_have_symlink:
                        print(f"  5. Symlink exists in all {len(uses)} utilizing skills? Yes")
                    else:
                        print(f"  5. Symlink exists in all utilizing skills? No.")
                        print(f"     -> Missing symlinks in: {', '.join(sorted(missing))}")
            else:
                pass # not specifically bound to a skill

        # Section: Missing Scripts
        missing_scripts = [s for s, data in skill_usage.items() if not data["physically_exists"]]
        
        # Apply whitelist filter
        filtered_missing_scripts = []
        global_ignores = set(whitelist.get("global_ignores", {}).keys())
        plugin_ignores = set(whitelist.get("plugin_ignores", {}).get(plugin_name, {}).keys())
        
        for s in missing_scripts:
            if s not in global_ignores and s not in plugin_ignores:
                filtered_missing_scripts.append(s)
                
        if filtered_missing_scripts:
            global_missing_summary[plugin_name] = []
            print(f"\n[!] MISSING OR UNRESOLVED SCRIPTS (See Global Summary below):")
            for s in sorted(filtered_missing_scripts):
                script_data = skill_usage[s]
                uses_set = script_data["skills"]
                if isinstance(uses_set, set):
                    uses = sorted(list(uses_set))
                else:
                    uses = []
                global_missing_summary[plugin_name].append((s, uses))
                print(f"      - {s} (Referenced by: {', '.join(uses)})")

    if global_missing_summary:
        print(f"\n\n{'='*70}")
        print("GLOBAL SUMMARY: MISSING SCRIPTS PER PLUGIN")
        print(f"{'='*70}")
        for plugin_name in sorted(list(global_missing_summary)):
            print(f"\n{plugin_name}:")
            for s, uses in global_missing_summary[plugin_name]:
                print(f"  - {s} (via: {', '.join(uses)})")

if __name__ == '__main__':
    # Calculate base_dir resolving upwards from plugins/agent-plugin-analyzer/scripts/analyzer.py
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    analyze_plugins(base_dir)
