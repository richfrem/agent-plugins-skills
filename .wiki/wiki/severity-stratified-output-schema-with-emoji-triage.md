---
concept: severity-stratified-output-schema-with-emoji-triage
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/severity-stratified-output.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.014727+00:00
cluster: list
content_hash: fa5ecfb125d03224
---

# Severity-Stratified Output Schema with Emoji Triage

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[severity-stratified-output]]
- [[severity-stratified-output]]
- [[severity-stratified-output]]
- [[severity-stratified-output]]
- [[severity-stratified-output]]
- [[severity-stratified-output]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/severity-stratified-output.md`
- **Indexed:** 2026-04-17T06:42:10.014727+00:00
