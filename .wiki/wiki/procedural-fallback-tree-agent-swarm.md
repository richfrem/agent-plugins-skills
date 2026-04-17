---
concept: procedural-fallback-tree-agent-swarm
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/agent-swarm/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.710603+00:00
cluster: action
content_hash: 7c3bc1f964a80f36
---

# Procedural Fallback Tree: Agent Swarm

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Agent Swarm

## 1. Rate Limit / Authentication Failure (Copilot)
If `./swarm_run.py --engine copilot` throws repeated 429s or authentication errors despite having a valid token:
- **Action**: Check the `--workers` flag. Overriding concurrency past `2` triggers GitHub's abuse filters which manifest as random auth failures. Reduce to `--workers 2`.
- **Secondary Action**: Ensure the token was loaded via `source ~/.zshrc`, not `gh auth token` (which lacks Copilot scopes).

## 2. Shared Cache / Concurrent Write Corruption
If the parallel workers are writing to a single JSON file and it becomes malformed or misses entries:
- **Action**: The `post_cmd` script lacks atomic locking. Temporarily switch to `--workers 1` to run the batch sequentially. For a permanent fix, rewrite the writer script to use `fcntl.flock` for atomic file operations. 

## 3. Worker Timeout Reached
If the `../scripts/swarm_run.py` script reports `Timeout` for specific files:
- **Action**: The work package is too large for the configured CLI agent. If using `haiku` or `gpt-5-mini`, re-run the job explicitly passing the failed files but bumping the `--timeout` parameter or switching to a heavier engine (`--engine claude`).

## 4. Checkpoint State File Corrupted
If the `--resume` flag fails because `.swarm_state_<job>.json` has phantom entries not matching the actual file system outputs:
- **Action**: Run the checkpoint reconciliation snippet from `./SKILL.md`. This clears the `completed` array of any files that aren't physically present in the output store, allowing the resume to proceed cleanly.


## See Also

- [[procedural-fallback-tree-create-azure-agent]]
- [[procedural-fallback-tree-create-sub-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]
- [[procedural-fallback-tree-link-checker-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/agent-swarm/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.710603+00:00
