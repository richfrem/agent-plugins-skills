# Procedural Fallback Tree: Red Team Review

## 1. Manifest Context is Too Large
If `context-bundler` generates a file too massive for the Red Team agent's context window:
- **Action**: Refine the `manifest.json`. Exclude massive unstructured logs or irrelevant boilerplate. Re-run the bundler. Adhere to the principle of "minimum viable context" for the reviewer.

## 2. Reviewer Persona is Missing
If instructed to use a specific persona (e.g., `personas/security/security-auditor.md`) but the file cannot be found:
- **Action**: Check the `personas/` directory to see if it was renamed. If completely missing, use a generic "Adversarial Code Reviewer" system prompt inline and notify the user that the specific persona file is missing.

## 3. Continuous Review Deadlock
If the Red Team agent rejects the research 3 or more times consecutively for the same core issue that cannot be resolved:
- **Action**: Break the loop. Bring the deadlocked specific disagreement to the Orchestrator/User for a tie-breaking executive decision. 

## 4. Unactionable Feedback
If the feedback returned from the reviewer is vague (e.g., "This isn't good enough"):
- **Action**: Do not loop back to research yet. Prompt the reviewer agent/human to quantify the failure using the Severity-Stratified schema (Critical/Moderate/Minor) with specific file/line references.
