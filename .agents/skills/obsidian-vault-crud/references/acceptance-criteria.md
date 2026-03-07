# Acceptance Criteria: Obsidian Vault CRUD

## 1. Atomic Write
- [ ] All file writes stage to `<target>.agent-tmp` first, then rename atomically via `os.rename()`.
- [ ] If any step fails, the `.agent-tmp` file is cleaned up and the error is reported.

## 2. Locking
- [ ] `.agent-lock` is created at vault root before any write batch.
- [ ] `.agent-lock` is removed after the write batch completes.
- [ ] If `.agent-lock` already exists, the agent reports and waits rather than overriding.

## 3. Concurrent Edit Detection
- [ ] `st_mtime` is captured before reading a file.
- [ ] `st_mtime` is checked again before writing. If changed, the write is aborted.

## 4. Frontmatter Fidelity
- [ ] `ruamel.yaml` is used exclusively — never `PyYAML`.
- [ ] YAML comments, indentation, and array styles are preserved after a round-trip.
