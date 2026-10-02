# Acceptance Criteria: vibe-behavioral-test-capture

## Correct Behaviors

- **Correct:** Vibe-behavioral-test-capture parses the prototype endpoints and visual discovery report to identify high-risk business logic components (e.g., pricing calculations, workflow states).
- **Correct:** Vibe-behavioral-test-capture records real HTTP traffic and inputs/outputs/side effects from active prototype interactions.
- **Correct:** Vibe-behavioral-test-capture generates executable characterization test files (e.g. Jest or Pytest specs) in `tests/characterization/`.
- **Correct:** Vibe-behavioral-test-capture asserts actual legacy output verbatim—including legacy bugs or quirky equations—to lock down exact baseline behavior.

## Incorrect Behaviors

- **Incorrect:** Vibe-behavioral-test-capture writes theoretical unit tests for hypothetical future classes rather than pinning down existing runtime behavior.
- **Incorrect:** Vibe-behavioral-test-capture attempts to "fix" bugs or sanitize payload structures inside the characterization tests.
- **Incorrect:** Vibe-behavioral-test-capture references abstract files or functions that do not run on the active codebase.
