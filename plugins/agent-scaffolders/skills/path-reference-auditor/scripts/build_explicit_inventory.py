import os
import json

PROJECT_ROOT = os.getcwd()
PLUGINS_DIR = os.path.join(PROJECT_ROOT, "plugins")

inventory = []
symlinks = []

print("Scanning plugins for all files and symlinks...")

for root, dirs, files in os.walk(PLUGINS_DIR):
    for name in files + dirs:
        # Skip hidden files
        if name.startswith("."):
            continue
            
        full_path = os.path.join(root, name)
        rel_path = os.path.relpath(full_path, PROJECT_ROOT)
        is_link = os.path.islink(full_path)
        
        entry = {
            "name": name,
            "path": rel_path,
            "is_symlink": is_link
        }
        
        if is_link:
            target = os.readlink(full_path)
            entry["target"] = target
            # link fails existence test if broken
            entry["is_broken"] = not os.path.exists(full_path)
            symlinks.append(entry)
        
        inventory.append(entry)

# Save Explicit Inventory
inventory_path = "/tmp/plugin_files_and_symlinks_inventory.json"
with open(inventory_path, "w") as f:
    json.dump(inventory, f, indent=2)

print(f"✅ Saved {len(inventory)} items to {inventory_path}")

# --- GAP ANALYSIS ---
print("Analyzing gaps and broken symlinks...")

# Find all physical files as correct candidates
physical_files_by_name = {}
for item in inventory:
    if not item["is_symlink"] and not os.path.isdir(os.path.join(PROJECT_ROOT, item["path"])):
        name = item["name"]
        if name not in physical_files_by_name:
            physical_files_by_name[name] = []
        physical_files_by_name[name].append(item["path"])

report_lines = [
    "# Broken Symlinks Repair Report",
    "",
    "| Current Symlink Location | Target points to | Correct Target Candidate | Status |",
    "|--------------------------|------------------|--------------------------|--------|",
]

fix_commands = ["#!/bin/bash", "echo 'Repairing symlinks...'"]

for link in symlinks:
    if link.get("is_broken", False):
        name = link["name"]
        loc = link["path"]
        target = link["target"]
        
        candidates = physical_files_by_name.get(name, [])
        mapped = "⚠️  Unknown target"
        fix_cmd = ""

        link_parts = loc.split("/")
        if "skills" in link_parts and "references" in link_parts:
             skill_name = link_parts[link_parts.index("skills") + 1]
             for cand in candidates:
                 if f"skills/{skill_name}/{name}" in cand:
                      mapped = f"`../{name}` (Skill Root)"
                      fix_cmd = f"ln -f -s '../{name}' '{loc}'"
                      break

        if fix_cmd == "" and candidates:
             plugin_name = link_parts[1]
             for cand in candidates:
                 if cand.startswith(f"plugins/{plugin_name}/references/{name}"):
                      mapped = f"`../../../references/{name}` (Plugin References)"
                      fix_cmd = f"ln -f -s '../../../references/{name}' '{loc}'"
                      break

        if fix_cmd == "" and candidates:
             for cand in candidates:
                 if "assets/" in cand:
                      mapped = f"Found elsewhere: {cand}"
                      break

        if fix_cmd != "":
             report_lines.append(f"| `{loc}` | `{target}` | {mapped} | ✅ Fixable |")
             fix_commands.append(f"ln -f -s '{mapped.split('`')[1]}' '{loc}'" if mapped.startswith("`") else fix_cmd)
        else:
             report_lines.append(f"| `{loc}` | `{target}` | {mapped} | ⚠️  Manual Fix |")

with open("/tmp/broken_symlinks_repair_report.md", "w") as f:
    f.write("\n".join(report_lines))

with open("/tmp/apply_symlink_repairs.sh", "w") as f:
    f.write("\n".join(fix_commands))

print("✅ Analysis Complete.")
print("Report: /tmp/broken_symlinks_repair_report.md")
print("Fix Script: /tmp/apply_symlink_repairs.sh")
