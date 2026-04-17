---
concept: priority-ordered-source-scanning
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/priority-ordered-scanning.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.014055+00:00
cluster: systems
content_hash: abab670563b91dbd
---

# Priority-Ordered Source Scanning

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Priority-Ordered Source Scanning

**Use Case:** Commands that search for entities across multiple systems (e.g., searching for a "Customer" in CRM, Billing, Support, and Email).

## The Core Mechanic

When querying multiple systems, do not treat all systems as equally authoritative. A contract in a CLM system supersedes an off-hand mention in a Slack message. The command must define a strict hierarchy of authority and execute searches in that order.

### Implementation Standard

In the command file, list the search steps in explicit priority order, and instruct the agent to halt or change its confidence if a higher-priority source contradicts a lower-priority one:

```markdown
## Step 2: Cross-System Entity Resolution

Search for the entity across all connected systems in this exact priority order:

1. **~~CLM (Authoritative)** - If found here, treat this as the ground truth name/status.
2. **~~CRM (Primary Context)** - Use for relationship status and account owner.
3. **~~Email (Recency)** - Use only for recent intent signals.
4. **~~Chat (Informal)** - Use only if no other context exists.
```


## See Also

- [[priority-ordered-scanning]]
- [[priority-ordered-scanning]]
- [[priority-ordered-scanning]]
- [[priority-ordered-scanning]]
- [[priority-ordered-scanning]]
- [[priority-ordered-scanning]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/priority-ordered-scanning.md`
- **Indexed:** 2026-04-17T06:42:10.014055+00:00
