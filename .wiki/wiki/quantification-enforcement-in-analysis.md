---
concept: quantification-enforcement-in-analysis
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/quantification-enforcement.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.014268+00:00
cluster: force
content_hash: 5bbfa333d473537d
---

# Quantification Enforcement in Analysis

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Quantification Enforcement in Analysis

**Use Case:** Research synthesis, data analysis, user feedback processing, or any command where the agent summarizes qualitative or quantitative data.

## The Core Mechanic

Agents tend to generate confident-sounding prose that conflates observation with interpretation ("The button is confusing" vs "5 users clicked the wrong button"). Embed strict epistemic guardrails into the output schema to force the agent to separate fact from inference and count instances before claiming prevalence.

### Implementation Standard

1. **Epistemic Rules**: Add instructions to the command's `Tips` section.
   ```markdown
   - **Separate observation from interpretation**: State what happened before stating what it means.
   - **Quantify**: Do not use vague terms like "most users". State "7 of 10 users".
   - **Anchor**: Use direct quotes or raw data points to anchor your insights.
   ```

2. **Template Enforcement**: Force quantification in the output schema.
   ```markdown
   ### Key Themes
   **Theme 1:** [Theme Description]
   **Prevalence:** [X of Y sources/users]
   **Anchor Quote:** "[Raw quote string from data]"
   ```

3. **Insight-to-Opportunity Mapping**: Force separation of synthesis from action.
   ```markdown
   | Insight (What we learned) | Opportunity (What we should do) |
   |---------------------------|---------------------------------|
   | [Observation]             | [Actionable next step]          |
   ```


## See Also

- [[quantification-enforcement]]
- [[quantification-enforcement]]
- [[quantification-enforcement]]
- [[quantification-enforcement]]
- [[quantification-enforcement]]
- [[quantification-enforcement]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/quantification-enforcement.md`
- **Indexed:** 2026-04-17T06:42:10.014268+00:00
