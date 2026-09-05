# Acceptance Criteria: repository-improvement

## ✅ Scenarios that must trigger
- "Synthesize a refactoring proposal from the friction hotspots."
- "What's the systemic fix for this recurring friction cluster?"
- "We keep hitting the same bug pattern — propose a real fix, not a patch."

## ❌ Scenarios that must NOT trigger
- "Open a PR for this fix." (requires human confirmation first, then `issue-pr-lifecycle-agent`)
- "Just patch this one line." (Tier 0 inline fix, not a systemic proposal)
- "Prioritize the github issue backlog." (use `github-issue-prioritizer`)
