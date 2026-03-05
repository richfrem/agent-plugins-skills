# Procedural Fallback Tree: Obsidian Vault CRUD

## 1. Lock File Present
If `.agent-lock` exists at vault root when starting a write operation:
- **Action**: Do NOT override the lock. Report it to the user, showing the lock file path and creation time. Wait for user confirmation before retrying. Never auto-delete the lock.

## 2. Atomic Write Failed (tmp not renamed)
If `os.rename()` fails after writing to `.agent-tmp`:
- **Action**: Clean up the `.agent-tmp` file. Report the failure with the OS error. Do NOT leave the `.agent-tmp` file in place. Do NOT attempt the write again without user confirmation.

## 3. Concurrent Edit Detected (mtime changed)
If `st_mtime` changed between read and intended write:
- **Action**: ABORT the write immediately. Report which file changed and ask the user to re-read the current content and confirm the intended change. Never proceed with a stale write.

## 4. ruamel.yaml Import Fails
If `import ruamel.yaml` raises `ImportError`:
- **Action**: Do NOT fall back to `PyYAML`. Report the missing dependency and provide the install command: `pip install ruamel.yaml`. Halt all CRUD operations until resolved.
