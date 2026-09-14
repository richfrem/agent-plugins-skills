# Procedural Fallback Tree: GitHub Issue Agent

## 1. GitHub CLI (`gh`) Unavailable
- **Condition**: `gh` binary missing or unauthenticated.
- **Action**: Emit dry-run payload to stdout or file so user can inspect or manually apply via web UI.

## 2. Taxonomy Validation Failure
- **Condition**: Supplied labels do not match `issue-taxonomy.json`.
- **Action**: Print missing required dimensions and suggest closest matching valid labels.

## 3. Secret Redaction Trigger
- **Condition**: Redaction scanner detects sensitive pattern in issue body.
- **Action**: Reject execution with specific line and matched pattern name; do not emit the secret into logs.
