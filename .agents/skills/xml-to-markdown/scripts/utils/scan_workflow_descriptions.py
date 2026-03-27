import os
import re

def scan_workflows(root_dir):
    print(f"Scanning {root_dir} for descriptions containing ':'...")
    print("-" * 60)
    
    issues_found = 0
    
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".md"):
                continue
                
            filepath = os.path.join(subdir, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                in_frontmatter = False
                frontmatter_count = 0
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    if line == "---":
                        frontmatter_count += 1
                        in_frontmatter = (frontmatter_count == 1)
                        continue
                        
                    if in_frontmatter and line.startswith("description:"):
                        # Extract value part
                        value = line[len("description:"):].strip()
                        
                        # Check for colon in value
                        if ":" in value:
                            # Heuristic: If it's quoted, it MIGHT be okay, but user asked to find ANY.
                            # We will mark unquoted ones as CRITICAL and quoted as INFO.
                            is_quoted = (value.startswith('"') and value.endswith('"')) or \
                                        (value.startswith("'") and value.endswith("'"))
                            
                            status = "WARNING (Unquoted)" if not is_quoted else "INFO (Quoted)"
                            
                            print(f"File: {filepath}")
                            print(f"  Line {i+1}: {line}")
                            print(f"  Status: {status}")
                            print("")
                            issues_found += 1
                            
                    if frontmatter_count >= 2:
                        break
                        
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print("-" * 60)
    print(f"Scan complete. Found potential issues in {issues_found} files.")

if __name__ == "__main__":
    # Use relative path since script run from root usually, 
    # but to be safe we can use absolute path or rely on cwd being root.
    # Assuming CWD is root of repo.
    target_dir = os.path.join(os.getcwd(), ".agent", "workflows")
    scan_workflows(target_dir)
