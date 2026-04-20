#!/usr/bin/env python
import os

files_to_fix = [
    "plugins/agent-agentic-os/skills/os-eval-backport/SKILL.md",
    "plugins/agent-agentic-os/skills/os-eval-lab-setup/SKILL.md",
    "plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md",
    "plugins/agent-agentic-os/skills/os-guide/SKILL.md",
    "plugins/agent-agentic-os/skills/os-improvement-report/SKILL.md",
    "plugins/agent-agentic-os/skills/os-init/SKILL.md",
    "plugins/agent-agentic-os/skills/os-memory-manager/SKILL.md",
    "plugins/agent-plugin-analyzer/skills/fix-plugin-paths/SKILL.md",
    "plugins/agent-scaffolders/skills/create-skill/SKILL.md",
    "plugins/excel-to-csv/skills/excel-to-csv/SKILL.md"
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"Not found: {filepath}")
        return
        
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    in_frontmatter = False
    in_description = False
    out_lines = []
    
    desc_lines = []
    
    for idx, line in enumerate(lines):
        if idx == 0 and line.strip() == '---':
            in_frontmatter = True
            out_lines.append(line)
            continue
            
        if in_frontmatter and line.strip() == '---':
            in_frontmatter = False
            # wrap up description
            if desc_lines:
                # clean up desc_lines
                desc_text = "".join(desc_lines)
                if len(desc_text) > 1000:
                    import re
                    # Remove all <commentary> blocks
                    desc_text = re.sub(r'<commentary>.*?</commentary>', '', desc_text, flags=re.DOTALL)
                    # If still > 1000, remove all <example> blocks
                    if len(desc_text) > 1000:
                         desc_text = re.sub(r'<example>.*?</example>', '', desc_text, flags=re.DOTALL)
                    # if still > 1000, truncate
                    if len(desc_text) > 1000:
                        desc_text = desc_text[:990] + "...\n"
                out_lines.append(desc_text)
                desc_lines = []
            out_lines.append(line)
            continue
            
        if in_frontmatter:
            if line.startswith('description:'):
                in_description = True
                out_lines.append(line)
            elif in_description:
                if not line.startswith(' ') and not line.startswith('\t') and ":" in line:
                    in_description = False
                    # wrap up description
                    if desc_lines:
                        desc_text = "".join(desc_lines)
                        if len(desc_text) > 1000:
                            import re
                            desc_text = re.sub(r'<commentary>.*?</commentary>', '', desc_text, flags=re.DOTALL)
                            if len(desc_text) > 1000:
                                desc_text = re.sub(r'<example>.*?</example>', '', desc_text, flags=re.DOTALL)
                            if len(desc_text) > 1000:
                                desc_text = desc_text[:990] + "...\n"
                        out_lines.append(desc_text)
                        desc_lines = []
                    out_lines.append(line)
                else:
                    desc_lines.append(line)
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)
            
    with open(filepath, 'w') as f:
        f.write("".join(out_lines))
    print(f"Fixed {filepath}")

def main():
    root_dir = '/Users/richardfremmerlid/Projects/agent-plugins-skills'
    for rel_path in files_to_fix:
        fix_file(os.path.join(root_dir, rel_path))

if __name__ == '__main__':
    main()
