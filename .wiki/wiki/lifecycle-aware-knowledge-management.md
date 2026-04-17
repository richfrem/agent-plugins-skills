---
concept: lifecycle-aware-knowledge-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/lifecycle-aware-knowledge.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.009865+00:00
cluster: artifacts
content_hash: 1e09e4a0941088d3
---

# Lifecycle-Aware Knowledge Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Lifecycle-Aware Knowledge Management

**Use Case:** Skills that produce durable artifacts like documentation, runbooks, templates, or knowledge base articles.

## The Core Mechanic

Treat artifacts not as static files, but as living documents with an explicit state machine and scheduled maintenance. This prevents documentation rot.

### Implementation Standard

1. **Define the State Machine in SKILL.md:**
   ```markdown
   | State | Meaning | Transition Trigger |
   |-------|---------|-------------------|
   | Draft | Created, needs review | — |
   | Published | Live, authoritative | Peer approval |
   | Needs Update | Flagged for revision | Product changes, customer confusion |
   | Archived | Preserved, not active | Superseded or outdated |
   | Retired | Removed | No longer relevant |
   ```

2. **Establish a Feedback Loop:**
   Instruct the agent to look for gaps during normal operations. For example, if a support skill answers a repeated question, it should automatically trigger the creation of a new KB article or flag the existing one as `Needs Update`.


## See Also

- [[lifecycle-aware-knowledge]]
- [[lifecycle-aware-knowledge]]
- [[lifecycle-aware-knowledge]]
- [[lifecycle-aware-knowledge]]
- [[lifecycle-aware-knowledge]]
- [[lifecycle-aware-knowledge]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/lifecycle-aware-knowledge.md`
- **Indexed:** 2026-04-17T06:42:10.009865+00:00
