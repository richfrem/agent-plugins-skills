---
concept: session-bootstrap
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-init/assets/templates/START_HERE_MD.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.177496+00:00
cluster: context
content_hash: 056383d2f23346a5
---

# Session Bootstrap

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Session Bootstrap

<!-- Run this at the start of each session to load context -->

## Load Context

1. @import context/soul.md (agent identity)
2. @import context/user.md (user preferences)
3. @import context/memory.md (last 20 facts)
4. Check context/memory/ for recent session logs (last 7 days)

## Check Open Items

Look for `[ ]` items in context/memory/ session logs from the last 7 days.

## Confirm Readiness

Say: "I am ready. Here is what I know: [brief summary of loaded context and open items]"


## See Also

- [[session-memory-manager]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[the-dual-mode-meta-skill-bootstrap-iteration]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[the-dual-mode-meta-skill-bootstrap-iteration]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-init/assets/templates/START_HERE_MD.md`
- **Indexed:** 2026-04-17T06:42:10.177496+00:00
