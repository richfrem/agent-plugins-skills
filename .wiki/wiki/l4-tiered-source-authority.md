---
concept: l4-tiered-source-authority
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/source-authority.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.015156+00:00
cluster: confidence
content_hash: e21f739446d7d3cf
---

# L4 Tiered Source Authority

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# L4 Tiered Source Authority
**Purpose:** Algorithmic translation of evidence quality into confidence scoring.
**Mechanics:**
1. Determine the maximum allowed `Confidence Level` (High, Medium, Low) based strictly on Source Tiers (T1=Authoritative, T2=Internal, T3=Chat/Informal).
2. Propagate this score to the final output.
3. If contradictions exist, favor the higher tier and downgrade confidence explicitly.


## See Also

- [[tiered-source-authority-with-propagated-confidence]]
- [[tiered-source-authority]]
- [[tiered-source-authority-with-propagated-confidence]]
- [[tiered-source-authority]]
- [[tiered-source-authority]]
- [[tiered-source-authority]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/source-authority.md`
- **Indexed:** 2026-04-17T06:42:10.015156+00:00
