---
concept: research-work-package-work-package-id-title
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/research/templates/task-prompt-template.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.344104+00:00
cluster: lane
content_hash: b60c2df2da0a74c5
---

# Research Work Package: {{work_package_id}} – {{title}}

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
work_package_id: "WPxx"
subtasks:
  - "Txxx"
title: "Replace with work package title"
phase: "Phase N - Replace with phase name"
lane: "planned"  # DO NOT EDIT - use: spec-kitty agent tasks move-task <WPID> --to <lane>
assignee: ""      # Optional friendly name when in doing/for_review
agent: ""         # CLI agent identifier (claude, codex, etc.)
shell_pid: ""     # PID captured when the task moved to the current lane
review_status: "" # empty | has_feedback | acknowledged (populated by reviewers/implementers)
reviewed_by: ""   # Agent ID of the reviewer (if reviewed)
history:
  - timestamp: "{{TIMESTAMP}}"
    lane: "planned"
    agent: "system"
    shell_pid: ""
    action: "Prompt generated via /spec-kitty.tasks"
---

# Research Work Package: {{work_package_id}} – {{title}}

## Review Feedback Status

**Read this first if you are working on this research task!**

- **Has review feedback?**: Check the `review_status` field above. If it says `has_feedback`, scroll to the **Review Feedback** section immediately (right below this notice).
- **You must address all feedback** before your work is complete. Feedback items are your research TODO list.
- **Mark as acknowledged**: When you understand the feedback and begin addressing it, update `review_status: acknowledged` in the frontmatter.
- **Report progress**: As you address each feedback item, update the Activity Log explaining what you changed.

---

## Review Feedback

> **Populated by `/spec-kitty.review`** – Reviewers add detailed feedback here when research needs revision. Each item must be addressed before returning for re-review.

*[This section is empty initially. Reviewers will populate it if the work is returned from review. If you see feedback here, treat each item as a must-do before completion.]*

---

## Markdown Formatting
Wrap HTML/XML tags in backticks: `` `<div>` ``, `` `<script>` ``
Use language identifiers in code blocks: ````python`, ````bash`

---

## Research Objectives & Success Criteria

- Summarize the exact outcomes that mark this research work package complete.
- Call out key acceptance criteria or quality metrics (e.g., minimum sources, confidence thresholds).

## Context & Methodology

- Reference prerequisite work and related documents.
- Link to supporting specs: `.kittify/memory/constitution.md`, `kitty-specs/.../plan.md` (methodology), `kitty-specs/.../spec.md` (research question), `research.md`, `data-model.md`.
- Highlight methodological constraints or quality requirements.

## Evidence Tracking Requirements

- **Source Register**: All sources MUST be recorded in `research/source-register.csv`
- **Evidence Log**: All findings MUST be recorded in `research/evidence-log.csv`
- **Citations**: Every claim must link to evidence rows

## Subtasks & Detailed Guidance

### Subtask TXXX – Replace with summary
- **Purpose**: Explain why this research subtask exists.
- **Steps**: Detailed, actionable instructions for conducting research.
- **Sources**: Types of sources to search (academic, industry, gray literature).
- **Output**: What artifact to update (source-register.csv, evidence-log.csv, findings.md).
- **Parallel?**: Note if this can run alongside others (e.g., different databases).
- **Quality Criteria**: Minimum requirements for this subtask.

### Subtask TYYY – Replace with summary
- Repeat the structure above for every included `Txxx` entry.

## Quality & Validation

- Specify minimum source requirements.
- Define confidence level thresholds.
- Document methodology adherence checkpoints.

## Risks & Mitigations

- List known pitfalls (bias, incomplete coverage, contradictory findings).
- Provide mitigation strategies.

## Review Guidance

- Key acceptance checkpoints for `/spec-kitty.review`.
- Methodology adherence verification points.
- Any context reviewers should consider.

## Activity Log

> **CRITICAL**: Activity log entries MUST be in chronological order (oldest first, newest last).

### How to Add Activity Log Entries

**When add

*(content truncated)*

## See Also

- [[work-package-prompt-work-package-id-title]]
- [[work-package-prompt-work-package-id-title]]
- [[spec-kittytasks-packages---generate-work-package-files]]
- [[spec-kittytasks-packages---generate-work-package-files]]
- [[work-packages-research-question]]
- [[spec-kittytasks-packages---generate-work-package-files]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/research/templates/task-prompt-template.md`
- **Indexed:** 2026-04-17T06:42:10.344104+00:00
