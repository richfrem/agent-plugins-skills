# Stage-Aware Feedback Modulation

**Use Case:** Any evaluation, review, or critique skill where the utility of the feedback depends heavily on *when* the artifact is being reviewed (e.g., Early Draft vs. Final Polish).

## The Core Mechanic

Instruct the agent to modulate its cognitive evaluation mode by adding a temporal dimension to the input context. The agent must first classify the "lifecycle stage" of the artifact before generating feedback.

### Implementation Standard

1. **Skill Definition**: Encode the stage considerations in the declarative `SKILL.md`.
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
