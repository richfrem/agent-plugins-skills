# WP07: Final Red Team Threat Assessment

**Goal**: Package the executed cryptographic results and the final POC architecture for a concluding Red Team review.

## Context
After the POC has been successfully executed and mathematically proven via `verify_poc.py`, we must package the entire project state and submit it to the Red Team to validate the premise of the "Manchurian Candidate" threat model (specifically the "consent gap" and "shadow features").

## Execution Steps

1. **Context Bundling**:
   - Use the `context-bundling` skill to package the entirety of `plugins/manchurian-candidate-poc/` including the code, rule definitions, and the cryptographic verification outputs.

2. **Draft the Assessment Prompt**:
   - Create `kitty-specs/001-manchurian-candidate-poc/research/red-team-assessment-prompt.md`.
   - The prompt should instruct the LLM (acting as the Red Team) to:
     - Review the benign utility of the tool.
     - Review the obfuscated payload execution mechanism.
     - Assess the severity of this vulnerability archetype in open agent ecosystems.
     - Detail why static analysis platforms often fail to catch these "shadow features."

3. **Execute Red Team Assessment**:
   - Use `claude-cli-agent` to pass the context bundle and the assessment prompt to the LLM.
   - Save the raw output to `kitty-specs/001-manchurian-candidate-poc/research/final-assessment.md`.
