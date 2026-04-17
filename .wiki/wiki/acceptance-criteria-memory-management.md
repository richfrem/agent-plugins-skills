---
concept: acceptance-criteria-memory-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/memory-management/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.118145+00:00
cluster: session
content_hash: f8cf91db6da3f927
---

# Acceptance Criteria: Memory Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Memory Management

## 1. Session Boot
- [ ] Hot cache files are loaded in the correct order: primer -> boot digest -> boot contract -> snapshot.
- [ ] Missing files are reported individually — the session does NOT silently continue without flagging the gap.
- [ ] Stale snapshot triggers a staleness warning, not a failure.

## 2. Promotion / Demotion
- [ ] Promotion occurs only when a knowledge item meets at least one promotion rule (3+ sessions, active constraint, identity anchor).
- [ ] Demotion moves knowledge to the correct deep storage directory — it is NEVER deleted.
- [ ] The agent confirms the promotion or demotion action with the user before writing.

## 3. Lookup Flow
- [ ] Queries traverse tiers in order: hot cache -> domain dir -> design docs -> semantic cache -> user.
- [ ] Each tier is checked before escalating to the next. The agent does NOT skip tiers.
- [ ] If knowledge is found at any tier, it is returned immediately without searching further tiers.

## 4. Session Seal
- [ ] Snapshot file is updated at session end with new learnings (1 sentence per file).
- [ ] No active task or constraint is left unsealed (not written to persistent storage).


## See Also

- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/memory-management/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.118145+00:00
