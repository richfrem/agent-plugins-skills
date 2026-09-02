# Acceptance Criteria: Red Team Review

## 1. Bundle Discipline
- [ ] Agent relies entirely on `context-bundler` and `manifest.json` to compile review packets, rather than manually `cat`ing files into prompts.
- [ ] Packets always include an explicit "Prompt" guiding the reviewer's focus.

## 2. Iteration Mandate
- [ ] Agent automatically parses the reviewer's verdict and correctly triggers the next loop iteration (Research vs Approval) based on that verdict.
- [ ] Agent refuses to manually override a negative or pending verdict to force an approval.

## 3. Delegation Limits
- [ ] As a specialized loop, it only manages the review cycle. It does not execute the actual implementation or dictate global repo state updates post-approval.
