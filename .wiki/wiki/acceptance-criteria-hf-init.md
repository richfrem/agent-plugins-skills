---
concept: acceptance-criteria-hf-init
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/hf-init/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.096278+00:00
cluster: token
content_hash: 254ab73222ee6a6c
---

# Acceptance Criteria: hf-init

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: hf-init

## 1. Credential Safety
- [ ] `HUGGING_FACE_TOKEN` is NEVER stored in `.env` or any committed file.
- [ ] Token is read exclusively from shell environment (not .env loader).
- [ ] Token is masked in all display output (first/last 4 chars only).

## 2. Validation
- [ ] All 4 required env vars (USERNAME, TOKEN, REPO, DATASET_PATH) are checked before any operation.
- [ ] `--validate-only` makes zero filesystem or API write calls.

## 3. Dataset Structure
- [ ] `ensure_dataset_structure()` creates `lineage/`, `data/`, `metadata/` on first run.
- [ ] Re-running init on an already-initialised dataset does NOT duplicate or corrupt the structure.


## See Also

- [[acceptance-criteria-os-init]]
- [[acceptance-criteria-hf-upload]]
- [[acceptance-criteria-obsidian-init]]
- [[acceptance-criteria-rlm-init]]
- [[acceptance-criteria-hf-upload]]
- [[acceptance-criteria-hf-upload]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/hf-init/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.096278+00:00
