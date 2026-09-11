# GitHub Issue Agent Operation Catalog

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
