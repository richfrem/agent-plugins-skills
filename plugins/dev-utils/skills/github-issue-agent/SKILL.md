---
name: github-issue-agent
plugin: dev-utils
description: >
  Agent skill for safe, dry-run-first, deduplicated, root-cause-consolidated, evidence-validated, and secret-redacted logging of repository execution friction into GitHub Issues.
  USE ONLY for durable repository bugs, execution friction (T1-T3), map debt, and architectural improvements.
  DO NOT USE for managing git worktrees (use `github-issue-worktree-agent`) or full PR lifecycles (use `github-issue-pr-lifecycle-agent`).
allowed_tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - multi_replace_file_content
  - grep_search
  - list_dir
---

# GitHub Issue Agent (github-issue-agent)

Provides safe, deduplicated, root-cause-consolidated, and taxonomy-validated logging of repository execution friction, map debt, and bugs into GitHub Issues.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Scope Boundary**: USE ONLY for durable repository bugs, execution friction (T1-T3), map debt, and architectural improvements. DO NOT USE for worktrees (use `github-issue-worktree-agent`) or PR lifecycles (use `github-issue-pr-lifecycle-agent`).
- **Dry-Run by Default**: All issue operations generate payloads in dry-run mode unless `--execute` is explicitly passed.
- **Secret Redaction Gate**: Submissions containing API keys, private tokens, or credentials are strictly blocked by `redaction_gate.py`.
- **Taxonomy Validation**: All issues require explicit dimensions: `type:*`, `tier:*`, `source:*`, `risk:*`, and `area:*` or `plugin:*`.
- **Structured Sections**: Bodies must include `## Summary`, `## Observed Behavior`, `## Expected Behavior`, `## Evidence`, and `## Impact`.

## Quick start

```bash
# Search related issues for deduplication
python3 plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_search.py \
  --title "Bug summary" --area-label "area:dev-utils"

# Generate validated issue payload (dry-run)
python3 plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py \
  --title "Bug summary" \
  --body "## Summary\n...\n## Observed Behavior\n...\n## Expected Behavior\n...\n## Evidence\n...\n## Impact\n..." \
  --labels "type:friction,tier:1-friction,source:agent,risk:low,area:dev-utils"
```

## Workflow

1. **Phase 1: Search & Deduplication**: Execute `gh_issue_search.py` using title keywords and area labels to consolidate into existing open issues.
2. **Phase 2: Payload Generation**: Structure the 5 mandatory markdown sections and assign the full taxonomy label set.
3. **Phase 3: Validation & Redaction**: Run `redaction_gate.py` and `body_validator.py` to ensure zero secrets and compliant formatting.
4. **Phase 4: Submission or Comment**: If root-cause exists, append evidence via `gh_issue_comment.py`; otherwise create new issue with `--execute`.

## Verification

```bash
# Validate taxonomy labels
python3 plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_taxonomy_validate.py \
  --labels "type:friction,tier:1-friction,source:agent,risk:low,area:dev-utils"

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/dev-utils/skills/github-issue-agent --mode source
```

## References
- [operation-catalog.md](references/operation-catalog.md) - CLI parameters and script usage catalog.
- [taxonomy-guide.md](references/taxonomy-guide.md) - Label taxonomy dimensions and definitions.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Verification gates and quality standards.
- [fallback-tree.md](references/fallback-tree.md) - Fallback recovery and offline procedures.
