---
concept: l4-artifact-lifecycle-state-machine
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/artifact-lifecycle.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.003731+00:00
cluster: flagged
content_hash: 65e69307754bb9b0
---

# L4 Artifact Lifecycle State Machine

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# L4 Artifact Lifecycle State Machine
**Purpose:** Manage the creation, publication, and deprecation of persistent knowledge.
**Mechanics:**
All durable artifacts (KB articles, standard responses) follow this state flow:
1. **Draft:** Created, pending peer/human review.
2. **Published:** Live and canonical.
3. **Needs Update:** Flagged by decay triggers (e.g. 6-months old, flagged by user workflow).
4. **Archived:** Preserved but inactive (superseded).
5. **Retired:** Deleted/Removed.


## See Also

- [[artifact-state-interrogative-routing]]
- [[artifact-lifecycle]]
- [[artifact-state-interrogative-routing]]
- [[artifact-state-interrogative-routing]]
- [[artifact-lifecycle]]
- [[artifact-state-interrogative-routing]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/artifact-lifecycle.md`
- **Indexed:** 2026-04-17T06:42:10.003731+00:00
