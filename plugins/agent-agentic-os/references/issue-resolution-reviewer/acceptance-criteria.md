# Acceptance Criteria: issue-resolution-reviewer

## ✅ Scenarios that must trigger
- "Audit the issues we closed last week for resolution quality."
- "Was this issue actually fixed or did it just get relabeled?"
- "Review issue resolution quality for the resolution:fixed label."

## ❌ Scenarios that must NOT trigger
- "Close this issue." (use `github-issue-agent`)
- "File a new github issue for this bug." (use `github-issue-agent`)
- "Prioritize the open issue backlog." (use `github-issue-prioritizer`)
