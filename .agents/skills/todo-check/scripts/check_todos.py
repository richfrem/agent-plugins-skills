import sys
import re
import os

def check_todos(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} not found.")
        return 1
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    todo_found = False
    for i, line in enumerate(lines, 1):
        if re.search(r'#.*TODO:', line, re.IGNORECASE) or re.search(r'//.*TODO:', line, re.IGNORECASE):
            print(f"{file_path}:{i}: {line.strip()}")
            todo_found = True
            
    if not todo_found:
        print(f"No TODOs found in {file_path}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_todos.py <file_path>")
        sys.exit(1)
    sys.exit(check_todos(sys.argv[1]))
