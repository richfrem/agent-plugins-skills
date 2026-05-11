import os
import re
from pathlib import Path

def count_ecosystem():
    plugins_dir = Path("plugins")
    ecosystem = {}
    
    for plugin_path in plugins_dir.iterdir():
        if plugin_path.is_dir():
            plugin_name = plugin_path.name
            skills_dir = plugin_path / "skills"
            agents_dir = plugin_path / "agents"
            commands_dir = plugin_path / "commands"
            
            skills = []
            if skills_dir.exists():
                skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
            
            agents = []
            if agents_dir.exists():
                agents = [f.stem for f in agents_dir.glob("*.md")]
                
            commands = []
            if commands_dir.exists():
                commands = [f.stem for f in commands_dir.glob("*.md")]
            
            ecosystem[plugin_name] = {
                "skills_count": len(skills),
                "agents_count": len(agents),
                "commands_count": len(commands),
                "skills": skills,
                "agents": agents,
                "commands": commands
            }
            
    return ecosystem

def update_readme(ecosystem):
    readme_path = Path("README.md")
    if not readme_path.exists():
        return
        
    with open(readme_path, "r", encoding='utf-8') as f:
        content = f.read()
        
    # Update plugin headers with skill counts
    # e.g., #### agent-scaffolders — Boilerplate & Audit (25 skills)
    for plugin_name, data in ecosystem.items():
        count = data["skills_count"]
        # Pattern to find the header for this plugin
        # We look for #### <plugin-name> followed by some text and (N skills)
        pattern = rf"(#### {re.escape(plugin_name)} .*?)\(\d+ skills\)"
        replacement = rf"\1({count} skills)"
        content = re.sub(pattern, replacement, content)
        
    # Summary stats at the top (if exists)
    total_plugins = len(ecosystem)
    total_skills = sum(d["skills_count"] for d in ecosystem.values())
    total_agents = sum(d["agents_count"] for d in ecosystem.values())
    
    # Update total counts if markers exist
    # Expecting markers like <!-- ECOSYSTEM_STATS_START --> ... <!-- ECOSYSTEM_STATS_END -->
    stats_marker = f"**Current Scale:** {total_plugins} Plugins · {total_skills} Skills · {total_agents} Sub-Agents"
    content = re.sub(r"<!-- ECOSYSTEM_STATS_START -->.*?<!-- ECOSYSTEM_STATS_END -->", 
                     f"<!-- ECOSYSTEM_STATS_START -->{stats_marker}<!-- ECOSYSTEM_STATS_END -->", 
                     content)

    with open(readme_path, "w", encoding='utf-8') as f:
        f.write(content)
        
    return total_plugins, total_skills, total_agents

if __name__ == "__main__":
    stats = count_ecosystem()
    p, s, a = update_readme(stats)
    print(f"[OK] README updated: {p} Plugins, {s} Skills, {a} Sub-Agents indexed.")
