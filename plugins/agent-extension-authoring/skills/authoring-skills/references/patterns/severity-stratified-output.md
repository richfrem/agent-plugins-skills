# Severity-Stratified Output Schema with Emoji Triage

**Use Case:** Review, audit, compliance, or critique commands that produce a list of findings or issues for a human to action.

## The Core Mechanic

Never output a flat list of issues. Instead, embed a strict, three-tier triage system directly into the markdown output template, using emoji to create immediate visual hierarchy.

### Implementation Standard

1. **The Output Template**:
   Use a markdown table with a dedicated severity column in the command file's `## Output` section. Do not let the agent invent severities; hardcode the exact labels it is allowed to use.

   ```markdown
   ## Output Template
   
   | Finding | Severity | Recommendation | Standards Reference |
   |---------|----------|----------------|---------------------|
   | [Issue] | 🔴 Critical / 🟡 Moderate / 🟢 Minor | [Fix] | [Rule/Criterion] |
   ```

2. **The Output Trailer**:
   Always end the audit output with an ordered "Priority Fixes" list to force the agent to rank the issues by importance, separated from the raw data table.

   ```markdown
   ### Priority Fixes
   1. [Most critical recommendation]
   2. [Second most critical]
   ```
