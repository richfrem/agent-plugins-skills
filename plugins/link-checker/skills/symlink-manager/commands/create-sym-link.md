---
name: create-sym-link
description: >
  Create a real symbolic link that works correctly on both Windows and macOS/Linux.
  Uses the symlink_manager.py script to automatically detect OS and create the 
  appropriate link type (symlink, junction, or hardlink fallback).
argument-hint: "[source-path] [dest-path]"
allowed-tools: Bash, Read
---

You are helping create a cross-platform symbolic link using the symlink_manager.py script.

### Step 1: Gather paths

If arguments were provided ($1 and $2), use them directly.

If no arguments, ask the user for:
1. **Source path** — relative to repo root (e.g., `plugins/my-plugin/scripts/script.py`)
2. **Destination path** — relative to repo root (e.g., `plugins/my-plugin/skills/my-skill/scripts/script.py`)

### Step 2: Validate paths
- [ ] Source exists: !`ls -l "$1" 2>&1`
- [ ] Destination parent directory exists
- [ ] Destination does not already exist (confirm if it does)

### Step 3: Execute the symlink manager script

Run the command (this uses the skill's copy of symlink_manager.py):
```bash
!`python ./scripts/symlink_manager.py create --src "$1" --dst "$2"`
```

**What the script does:**
- **Windows with Developer Mode enabled**: Creates true symlink
- **Windows without Developer Mode**: Falls back to junction (dirs) or hardlinks (files)
- **macOS/Linux**: Always creates true symlinks
- **All platforms**: Uses relative paths for portability
- **Manifest**: Automatically updates `symlinks.json` for restoration

### Step 4: Verify and suggest commit

After successful creation:
- Report the symlink was created with relative path: !`readlink "$2"`
- Verify file is accessible: !`head -3 "$2" 2>&1 || echo "Link points to: $(readlink "$2")"`
- Suggest: `git add "$2" && git commit -m "feat: add symlink for $2"`

### Special case: Windows without Developer Mode
- If user sees hardlink fallback, they can enable Developer Mode:
  Settings → System → For Developers → toggle Developer Mode ON
- Alternatively, run as administrator for unprivileged symlink creation
- Warn: Hardlinks are not cross-platform compatible
