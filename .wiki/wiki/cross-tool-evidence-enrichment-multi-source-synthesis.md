---
concept: cross-tool-evidence-enrichment-multi-source-synthesis
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/multi-source-synthesis.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.011587+00:00
cluster: plugin-code
content_hash: e8202d54d7622a90
---

# Cross-Tool Evidence Enrichment (Multi-Source Synthesis)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Cross-Tool Evidence Enrichment (Multi-Source Synthesis)

**Use Case:** Complex analysis commands that can pull context from multiple upstream systems and push outputs to multiple downstream systems simultaneously.

## The Core Mechanic

When defining the `## If Connectors Available` section, do not write generic "use tools if available" blocks. Instead, explicitly assign one of three distinct **roles** to each tool category in the synthesis pipeline: Source, Validator, or Publisher.

### Implementation Standard

1. **Source (Input Enrichment)**: Pulls data to build the foundation.
   ```markdown
   If **~~user feedback** is connected:
   - Pull the last 30 days of support tickets to supplement interview data.
   ```

2. **Validator (Cross-Reference)**: Used to verify qualitative claims against quantitative metrics.
   ```markdown
   If **~~product analytics** is connected:
   - Validate qualitative "difficulty" findings by checking actual task completion rates.
   ```

3. **Publisher (Output Routing)**: Automates the "next step" actionability of the report.
   ```markdown
   If **~~project tracker** is connected:
   - Create individual tickets for each 🔴 Critical finding identified above.
   ```


## See Also

- [[multi-source-synthesis]]
- [[multi-source-synthesis]]
- [[multi-source-synthesis]]
- [[multi-source-synthesis]]
- [[multi-source-synthesis]]
- [[multi-source-synthesis]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/multi-source-synthesis.md`
- **Indexed:** 2026-04-17T06:42:10.011587+00:00
