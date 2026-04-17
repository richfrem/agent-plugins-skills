---
concept: stage-aware-feedback-modulation
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/stage-aware-feedback.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.015615+00:00
cluster: plugin-code
content_hash: 96a3181d636639cd
---

# Stage-Aware Feedback Modulation

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Stage-Aware Feedback Modulation

**Use Case:** Any evaluation, review, or critique skill where the utility of the feedback depends heavily on *when* the artifact is being reviewed (e.g., Early Draft vs. Final Polish).

## The Core Mechanic

Instruct the agent to modulate its cognitive evaluation mode by adding a temporal dimension to the input context. The agent must first classify the "lifecycle stage" of the artifact before generating feedback.

### Implementation Standard

1. **Skill Definition**: Encode the stage considerations in the declarative `././SKILL.md`.
   ```markdown
   ## Stage Considerations
   - **Exploration Stage:** Focus on structural issues, logic, and broad concepts. Ignore minor typos or exact formatting.
   - **Refinement Stage:** Focus on consistency, edge cases, and missing workflows.
   - **Final Polish:** Focus on exact wording, accessibility checks, and pixel-perfect/syntax-perfect validation.
   ```

2. **Command Input Gathering**: Require the user to specify the stage when invoking the procedural command.
   ```markdown
   ## What I Need From You
   Please provide the artifact AND specify its current stage: (Exploration / Refinement / Final).
   ```


## See Also

- [[stage-aware-feedback]]
- [[stage-aware-feedback]]
- [[stage-aware-feedback]]
- [[stage-aware-feedback]]
- [[stage-aware-feedback]]
- [[stage-aware-feedback]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/stage-aware-feedback.md`
- **Indexed:** 2026-04-17T06:42:10.015615+00:00
