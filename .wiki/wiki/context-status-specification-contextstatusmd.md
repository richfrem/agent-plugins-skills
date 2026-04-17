---
concept: context-status-specification-contextstatusmd
source: plugin-code
source_file: agent-agentic-os/references/memory/status-file-spec.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.139152+00:00
cluster: file
content_hash: 5618a91acab011f8
---

# Context Status Specification (`context/status.md`)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Context Status Specification (`context/status.md`)

The `status.md` file serves as the "active register" and the primary interface point between human users and the autonomous heartbeat loops. 

## Strict Format Requirements
To ensure the `~~scheduler` heartbeat agents (`Triple-Loop Retrospective`, etc.) can reliably parse state, `status.md` must adhere to the following markdown structure.

```markdown
---
last_updated: YYYY-MM-DDTHH:MM:SSZ
phase: [Phase Name / Project Milestone]
---
# Current Status

## Active Task
- The single current task the team is working on right now. Keep it brief.

## Blockers
- Any immediate blockers. If none, write "None".

## Next Steps
- Step 1
- Step 2

## Heartbeat Queue
- [ ] Task for the hourly tick to pick up
- [ ] Another async background task
```

## Parsing Rules
1. Agents should `Read` this file **before** executing background loops.
2. Agents must update the `last_updated` YAML frontmatter field via `python3 context/kernel.py state_update last_updated <timestamp>` whenever they mutate the queue or blocks.
3. Keep the file small—do not use this file for architectural rules or logs (that is what the memory tiers are for).


## See Also

- [[current-status]]
- [[context-folder-patterns]]
- [[improvement-ledger-specification]]
- [[quick-start-zero-context-guide]]
- [[context-folder-patterns]]
- [[context-folder-patterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/references/memory/status-file-spec.md`
- **Indexed:** 2026-04-17T06:42:09.139152+00:00
