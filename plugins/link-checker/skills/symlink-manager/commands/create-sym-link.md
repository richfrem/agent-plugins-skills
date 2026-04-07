---
name: create-sym-link
description: >
  Create a real symbolic link that works correctly on both Windows and macOS/Linux.
  Automatically detects the OS and creates the appropriate link type. Use whenever
  you need to create cross-platform symlinks that Git will recognize correctly.
argument-hint: "[source-path] [dest-path]"
allowed-tools: Bash, Read
---

You are helping create a cross-platform symbolic link. The process automatically adapts to the OS:

**On macOS/Linux:** Creates true symlinks (`ln -s`)
**On Windows:** Creates true symlinks if Developer Mode is enabled, otherwise uses fallback strategies

### Step 1: Gather paths
If arguments were provided, use them:
- Source: $1
- Destination: $2

If no arguments, ask the user for:
1. **Source path** — the file or directory the link should point to (relative to repo root)
2. **Destination path** — where the symlink should be created (relative to repo root)

### Step 2: Validate
- [ ] Source path exists: `ls -l <source>`
- [ ] Destination directory exists
- [ ] Destination file does NOT already exist (ask before overwriting)
- [ ] Both paths are relative from repo root

### Step 3: Create using the symlink manager script
The script automatically detects OS and handles platform differences:

```bash
python ./scripts/symlink_manager.py create --src <source> --dst <destination>
```

This uses `symlink_manager.py` which:
- **Windows with Developer Mode**: creates true symlinks
- **Windows without Developer Mode**: falls back to junction (dirs) or hardlinks (files)
- **macOS/Linux**: always creates true symlinks
- Updates `symlinks.json` manifest automatically

### Step 4: Verify and commit
1. Check the created link: `ls -la <destination>` should show link arrow `->` or symlink info
2. Suggest commit: `git add <destination> && git commit -m "feat: add symlink <name>"`

### Special case: If user is on Windows
- If they see hardlink fallback, suggest enabling Developer Mode for proper symlinks:
  Settings → System → For Developers → toggle Developer Mode ON
- Hardlinks created as fallback work but are not cross-platform compatible
