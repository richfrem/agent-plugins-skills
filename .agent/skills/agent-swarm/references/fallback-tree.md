# Procedural Fallback Tree: Agent Swarm

## 1. Rate Limit / Authentication Failure (Copilot)
If `swarm_run.py --engine copilot` throws repeated 429s or authentication errors despite having a valid token:
- **Action**: Check the `--workers` flag. Overriding concurrency past `2` triggers GitHub's abuse filters which manifest as random auth failures. Reduce to `--workers 2`.
- **Secondary Action**: Ensure the token was loaded via `source ~/.zshrc`, not `gh auth token` (which lacks Copilot scopes).

## 2. Shared Cache / Concurrent Write Corruption
If the parallel workers are writing to a single JSON file and it becomes malformed or misses entries:
- **Action**: The `post_cmd` script lacks atomic locking. Temporarily switch to `--workers 1` to run the batch sequentially. For a permanent fix, rewrite the writer script to use `fcntl.flock` for atomic file operations. 

## 3. Worker Timeout Reached
If the `swarm_run.py` script reports `Timeout` for specific files:
- **Action**: The work package is too large for the configured CLI agent. If using `haiku` or `gpt-5-mini`, re-run the job explicitly passing the failed files but bumping the `--timeout` parameter or switching to a heavier engine (`--engine claude`).

## 4. Checkpoint State File Corrupted
If the `--resume` flag fails because `.swarm_state_<job>.json` has phantom entries not matching the actual file system outputs:
- **Action**: Run the checkpoint reconciliation snippet from `SKILL.md`. This clears the `completed` array of any files that aren't physically present in the output store, allowing the resume to proceed cleanly.
