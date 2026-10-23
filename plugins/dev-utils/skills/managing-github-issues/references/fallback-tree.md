# Procedural Fallback Tree: managing-github-issues

## `log` mode
### 1. GitHub CLI (`gh`) Unavailable
- **Condition**: `gh` binary missing or unauthenticated.
- **Action**: Emit dry-run payload to stdout or file so user can inspect or manually apply via web UI.

### 2. Taxonomy Validation Failure
- **Condition**: Supplied labels do not match `issue-taxonomy.json`.
- **Action**: Print missing required dimensions and suggest closest matching valid labels.

### 3. Secret Redaction Trigger
- **Condition**: Redaction scanner detects sensitive pattern in issue body.
- **Action**: Reject execution with specific line and matched pattern name; do not emit the secret into logs.

## `backlog` mode
### 1. Task File Missing or Unreadable
- **Condition**: `--task-path` does not point to an existing readable markdown file.
- **Action**: Terminate with clear path error message; prompt user to supply valid task file.

### 2. GitHub CLI (`gh`) Unavailable
- **Condition**: Live execution requested (`--execute`) but `gh` CLI unavailable or unauthenticated.
- **Action**: Output payload JSON to stdout and inform user to install `gh` or create the issue manually.

### 3. Redaction Failure
- **Condition**: Secret token discovered in task file content.
- **Action**: Abort immediately without printing the secret; indicate line number for manual remediation.

## `prioritize` mode
### 1. Missing Tier or Blocker Information
- **Condition**: Issue has no `tier:*` or blocker labels.
- **Action**: Assess occurrence frequency; if absent, default rank safely to `P3` (Low Priority).

### 2. Invalid GraphQL Project ID
- **Condition**: GitHub Projects v2 `project_id` or `item_id` format invalid or inaccessible.
- **Action**: Output calculated priority label directly to stdout so priority can be applied via standard issue labels (`gh issue edit --add-label`).

## `propose-refactor` mode
1. Synthesize hotspot clusters into a refactor proposal for human review -> 2. If cluster data is insufficient, report the raw friction list without synthesis.

## `review-resolution` mode
1. Audit closed issue against resolution criteria -> 2. If criteria undocumented, fall back to generic root-cause-resolved heuristic and flag reduced confidence.
