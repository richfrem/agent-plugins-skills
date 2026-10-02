# Procedural Fallback Tree: Ecosystem Authoritative Sources

## 1. Missing Reference Target
If the table of contents links to a `reference/` file that does not physically exist in the filesystem:
- **Action**: Do not attempt to guess the specification contents. Explicitly state to the user: "The authoritative source file for [Topic] is missing." Fall back to the main repository `README.md` to see if the knowledge was moved globally.

## 2. Conflicting Specifications
If asked a question where the specs in this plugin contradict the global `constitution.md` (e.g., execution rules):
- **Action**: The global `constitution.md` ALWAYS wins. Surface the contradiction to the user and explicitly prioritize the constitutional mandate over the plugin's local reference docs.

## 3. Spec Interpretation Deadlock
If the user repeatedly argues that a generated artifact aligns with the specs, but the agent believes it fails:
- **Action**: Defer to the `ecosystem-standards` skill. Do not debate the user. Run a formal audit against the specific component to get an objective pass/fail checklist.

## 4. Unsupported Ecosystem Query
If asked about a framework pattern (e.g., "CrewAI") not covered by the authoritative sources:
- **Action**: Explicitly state that the framework is not part of the local Open Standard ecosystem. Do not try to map proprietary Claude Plugin constraints onto unsupported engines.
