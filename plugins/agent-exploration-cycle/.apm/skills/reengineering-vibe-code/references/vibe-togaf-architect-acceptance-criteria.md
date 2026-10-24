# Acceptance Criteria: vibe-togaf-architect

## Correct Behaviors

- **Correct:** Vibe-togaf-architect reads both the `DISCOVERY_REPORT.md` and NFR responses from the context before generating specifications.
- **Correct:** Vibe-togaf-architect generates all 5 required spec files (`REQUIREMENTS.md`, `SYSTEM_CONTEXT.md`, `SEQUENCE_DIAGRAMS.md`, `TECH_MAPPING.md`, `DEPLOYMENT.md`) inside the `/specs` folder.
- **Correct:** Vibe-togaf-architect creates syntactic-valid Mermaid diagrams that map system dependencies and sequence charts.
- **Correct:** Vibe-togaf-architect pauses execution immediately after scaffolding `/specs` and enforces the **🛑 TIER GATE** to request explicit user sign-off.

## Incorrect Behaviors

- **Incorrect:** Vibe-togaf-architect generates incomplete specifications (e.g. omitting sequence flows or tech maps).
- **Incorrect:** Vibe-togaf-architect proceeds with sandbox scaffolding or handoff scripts before the user has given explicit approval at the Risk Gate.
- **Incorrect:** Vibe-togaf-architect writes malformed Mermaid tags that break rendering in standard browsers or viewers.
