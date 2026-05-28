# Acceptance Criteria: vibe-spec-packager

## Correct Behaviors

- **Correct:** Vibe-spec-packager parses the approved stack configurations inside `specs/TECH_MAPPING.md` before initiating directory creation.
- **Correct:** Vibe-spec-packager consolidates requirements, system context diagram, and database configurations into a single-file `specs/spec-kit.md`.
- **Correct:** Vibe-spec-packager creates the fundamental repository folders (`src/`, `tests/`, `config/`) and configuration templates matching the approved stacks.
- **Correct:** Vibe-spec-packager provides clear, actionable instructions for executing downstream builders (e.g. `obra/superpowers`) utilizing the spec-kit.

## Incorrect Behaviors

- **Incorrect:** Vibe-spec-packager hardcodes generic backend structures that deviate from the technology stack configured inside `specs/TECH_MAPPING.md`.
- **Incorrect:** Vibe-spec-packager overwrites pre-existing project code or makes destructive folder wipes without safety checks.
- **Incorrect:** Vibe-spec-packager hands off control without providing command line templates to run the final engineering harness.
