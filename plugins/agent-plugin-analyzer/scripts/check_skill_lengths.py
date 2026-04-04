#!/usr/bin/env python3
import os
import glob

def get_description_length(filepath):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        in_frontmatter = False
        in_description = False
        desc_content = ""
        
        for idx, line in enumerate(lines):
            if idx == 0 and line.strip() == '---':
                in_frontmatter = True
                continue
                
            if in_frontmatter and line.strip() == '---':
                break
                
            if in_frontmatter:
                if line.startswith('description:'):
                    in_description = True
                    # Get what's after 'description:'
                    after_colon = line.split(':', 1)[1].strip()
                    if after_colon not in ('>', '|', '>-', '|-'):
                        desc_content += after_colon + "\n"
                elif in_description:
                    # If we hit another root-level key, we are out of the description
                    if not line.startswith(' ') and not line.startswith('\t') and ":" in line:
                        in_description = False
                    else:
                        desc_content += line
                        
        if desc_content:
            return len(desc_content.strip())
            
    except Exception as e:
        pass
    return -1

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugins_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
    
    pattern = os.path.join(plugins_dir, '**', 'SKILL.md')
    files = glob.glob(pattern, recursive=True)
    
    print(f"Checked {len(files)} SKILL.md files. Highlighting near limit (> 800) and failed (> 1024):")
    passed = []
    failed = []
    ok_os_skills = []
    
    for filepath in sorted(files):
        length = get_description_length(filepath)
        if length > 0:
            short_path = filepath.split('plugins/')[1] if 'plugins/' in filepath else filepath
            if length > 1024:
                failed.append(f"[FAIL] {length} chars -> {short_path}")
            elif length > 800:
                passed.append(f"[OK]   {length} chars -> {short_path}")
            elif "os-" in short_path:
                ok_os_skills.append(f"[OK]   {length} chars -> {short_path}")
                
    for msg in failed:
        print(msg)
    if not failed:
        print("\nAll skill descriptions are under the 1024 character limit! 🎉")
        
    print("\nFiles > 800 chars:")
    for msg in passed:
        print(msg)
        
    print("\nRecently updated OS skills (length < 800):")
    for msg in ok_os_skills:
        print(msg)

if __name__ == '__main__':
    main()
