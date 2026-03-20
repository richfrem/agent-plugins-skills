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
