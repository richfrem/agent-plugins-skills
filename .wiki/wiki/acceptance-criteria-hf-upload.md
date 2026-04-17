---
concept: acceptance-criteria-hf-upload
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/hf-upload/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.097355+00:00
cluster: valence
content_hash: 984565b4a86db337
---

# Acceptance Criteria: hf-upload

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: hf-upload

## 1. Prerequisite Gate
- [ ] All upload operations verify valid credentials via hf_config before executing.
- [ ] Upload is aborted (not silently skipped) if credentials are invalid.

## 2. Retry Behavior
- [ ] Rate-limit errors (429) trigger exponential backoff with up to 5 retries.
- [ ] Each retry attempt is logged/reported. Failures after 5 attempts surface as errors.

## 3. Result Verification
- [ ] Every upload operation returns and checks `HFUploadResult.success`.
- [ ] A failed upload (success=False) is always reported with the `error` message.

## 4. Valence Filtering
- [ ] `upload_soul_snapshot()` rejects uploads with valence below `SOUL_VALENCE_THRESHOLD`.
- [ ] Rejection includes the valence score, threshold value, and does NOT silently drop the content.


## See Also

- [[acceptance-criteria-hf-init]]
- [[acceptance-criteria-hf-init]]
- [[acceptance-criteria-hf-init]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/hf-upload/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.097355+00:00
