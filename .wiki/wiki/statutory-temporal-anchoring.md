---
concept: statutory-temporal-anchoring
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/temporal-anchoring.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.016489+00:00
cluster: knowledge
content_hash: d8d7af458a6bbbea
---

# Statutory Temporal Anchoring

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Statutory Temporal Anchoring

**Use Case:** Compliance, Legal, Security, or heavily regulated domains where the "truth" changes over time based on external regulations.

## The Core Mechanic

Domain knowledge codified in a `././SKILL.md` degrades over time. If a skill states "Breach notification is required within 72 hours," it becomes silently wrong if the law changes. Instead, anchor every factual numeric claim to its specific legal, regulatory, or policy source version.

### Implementation Standard

In the declarative domain knowledge of the skill, forbid "naked numbers".

```markdown
## Regulatory Standards

- **Breach notification**: Notify supervisory authority within **72 hours** (Source: GDPR Article 33).
- **Records of processing**: Maintain records of processing activities (Source: GDPR Article 30).
- **Standard Contractual Clauses**: Use the **June 2021 version** of the EU SCCs.
```

This allows human auditors (or other agent verification scripts) to verify the freshness of the knowledge without having to guess where the constraints came from.


## See Also

- [[temporal-anchoring]]
- [[temporal-anchoring]]
- [[temporal-anchoring]]
- [[temporal-anchoring]]
- [[temporal-anchoring]]
- [[temporal-anchoring]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/temporal-anchoring.md`
- **Indexed:** 2026-04-17T06:42:10.016489+00:00
