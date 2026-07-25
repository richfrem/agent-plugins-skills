---
name: github-issue-agent
plugin: dev-utils
description: >
  Agent skill for safe, dry-run-first, deduplicated, root-cause-consolidated, evidence-validated, and secret-redacted logging of repository execution friction into GitHub Issues.
  USE ONLY for durable repository bugs, execution friction (T1-T3), map debt, and architectural improvements.
  DO NOT USE for temporary intra-session checklists (use task-agent instead).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue Agent (`github-issue-agent`)

> **Routing Directive:** USE ONLY for durable repository bugs, execution friction (T1-T3), map debt, and architectural improvements. DO NOT USE for temporary intra-session checklists (use `task-agent` instead).

The `github-issue-agent` skill provides a safe, standardized interface for querying, searching, creating, commenting on, and validating GitHub Issues stemming from agent execution friction, map debt, bugs, and system improvements.

---

## Dry-Run Default Execution Contract

> [!IMPORTANT]
> **Safety First:** By default, all issue-modifying operations (issue creation, commenting, label edits) execute in **dry-run / payload-generation mode** (`execute=False`).
> No live mutation occurs unless `execute=True` is explicitly passed and all safety gates pass.

Before any GitHub issue is created or updated, the request passes through three mandatory security and quality gates:
1. **Secret Redaction Gate** (`redaction_gate.py`): Scans titles and bodies for tokens, API keys, private keys, or credentials. Blocks execution if detected.
2. **Taxonomy Validation Gate** (`gh_issue_taxonomy_validate.py`): Enforces `issue-taxonomy.json` constraints. Requires `type:*`, `tier:*`, `source:*`, `risk:*`, AND location (`area:*` OR `plugin:*`).
3. **Evidence Quality Body Validation Gate** (`body_validator.py`): Requires standard structured markdown sections (`## Summary`, `## Observed Behavior`, `## Expected Behavior`, `## Evidence`, `## Impact`).

---

## Operation Catalog

### 1. `create-friction-issue`
Scaffolds and submits (or outputs payload for) a friction issue resulting from agent execution friction or tool failure.

- **Helper Script:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py`
- **Default Labels Required:** `type:friction`, `tier:1-friction` (or `tier:2-structural` / `tier:3-architecture`), `source:agent`, `risk:low` (or appropriate risk level), plus location (`area:*` or `plugin:*`).
- **Input Parameters:**
  - `title`: Short, clear summary of root-cause friction.
  - `body`: Markdown content conforming to required sections.
  - `labels`: List of taxonomy labels matching `issue-taxonomy.json`.
  - `execute`: Boolean (`False` for dry-run payload generation, `True` for live creation via `gh`).

### 2. `create-map-debt-issue`
Converts an entry from `map-debt.md` into a formal tracked GitHub issue.

- **Helper Script:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py`
- **Default Labels Required:** `type:map-debt`, `tier:*`, `source:agent`, `risk:*`, location (`area:*` or `plugin:*`).

### 3. `create-bug-issue`
Logs a verified bug or code defect identified during execution or test failure.

- **Helper Script:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py`
- **Default Labels Required:** `type:bug`, `tier:*`, `source:agent`, `risk:*`, location (`area:*` or `plugin:*`).

### 4. `search-related-issues`
Searches open and closed issues for existing root-cause items to prevent duplicate issues.

- **Helper Script:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_search.py`
- **Input Parameters:**
  - `title`: Proposed issue title or keyword.
  - `area_label`: Location label (`area:*` or `plugin:*`).
  - `file_paths`: List of affected file paths.
- **Output:** Returns JSON object indicating if an existing root cause exists (`has_existing_root_cause`), target issue number (`target_issue_number`), and action recommendation (`comment_and_append_evidence` vs `create_new_issue`).

### 5. `comment-on-existing-issue`
Appends additional empirical evidence, stack traces, or context to an existing issue rather than opening a duplicate.

- **Helper Script:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_comment.py`
- **Input Parameters:**
  - `issue_number`: GitHub issue ID.
  - `comment_body`: Markdown comment text (must pass secret redaction scan).
  - `execute`: Boolean (`False` for dry-run payload generation, `True` for live comment posting).

### 6. `validate-issue-taxonomy`
Validates a list of labels against `issue-taxonomy.json`.

- **Helper Script:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_taxonomy_validate.py`
- **Usage:** Run CLI or import `validate_taxonomy(labels: list[str])`.

---

## Taxonomy Reference

Taxonomy labels and rules are defined in `plugins/dev-utils/skills/github-issue-agent/issue-taxonomy.json`.

Mandatory dimensions for every issue:
- `type`: `type:bug`, `type:friction`, `type:map-debt`, `type:enhancement`, `type:documentation`, `type:security`, `type:architecture`, `type:test-gap`
- `tier`: `tier:0-quickfix`, `tier:1-friction`, `tier:2-structural`, `tier:3-architecture`
- `source`: `source:agent`, `source:human`, `source:script`, `source:test`, `source:review`, `source:migration`
- `risk`: `risk:low`, `risk:medium`, `risk:high`, `risk:security-sensitive`, `risk:destructive-operation`
- `location`: Must have at least one `area:*` label or one `plugin:*` label.
