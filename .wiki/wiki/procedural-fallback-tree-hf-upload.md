---
concept: procedural-fallback-tree-hf-upload
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/hf-upload/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.097563+00:00
cluster: action
content_hash: 8e580831965c8f5d
---

# Procedural Fallback Tree: hf-upload

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: hf-upload

## 1. hf-init Not Run (Credentials Not Configured)
If `hf_config.py` validation fails before an upload:
- **Action**: HALT. Do NOT attempt any upload. Report that hf-init must be run first. Provide the init command.

## 2. Rate Limit (429) After 5 Backoff Retries
If all 5 exponential backoff retry attempts are exhausted:
- **Action**: Report the final failure with the upload target and error details. Do NOT silently drop the upload. Ask the user to retry manually later or check HF API status.

## 3. HFUploadResult.success is False
If any upload operation returns `success=False`:
- **Action**: Report the `error` field from the result. Do NOT proceed to downstream operations that depend on this upload. Ask user whether to retry or abort.

## 4. Valence Filter Rejection
If `upload_soul_snapshot()` is called with valence below `SOUL_VALENCE_THRESHOLD`:
- **Action**: Report the exact valence score and the configured threshold. Do NOT upload. Ask the user to review the content or override the threshold explicitly.


## See Also

- [[procedural-fallback-tree-hf-init]]
- [[procedural-fallback-tree-hf-init]]
- [[procedural-fallback-tree-hf-init]]
- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/hf-upload/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.097563+00:00
