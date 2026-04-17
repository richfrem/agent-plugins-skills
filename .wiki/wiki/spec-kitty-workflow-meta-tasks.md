---
concept: spec-kitty-workflow-meta-tasks
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/spec-kitty-meta-tasks.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.368031+00:00
cluster: feature
content_hash: fe0390c11ab32883
---

# Spec Kitty Workflow Meta-Tasks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Spec Kitty Workflow Meta-Tasks
<!-- To be included in Session Task List for any Feature Work -->

## Phase A: Workflow Management (Use CLI, No Manual Edits)
- [ ] **Check Prerequisites**: `spec-kitty agent feature feature-check-prerequisites`
- [ ] **Specify Feature**: `/spec-kitty.specify` (Generates `spec.md`)
- [ ] **Plan Implementation**: `/spec-kitty.plan` (Generates `plan.md`)
- [ ] **Generate Tasks**: `/spec-kitty.tasks` (Generates `tasks/WP-*.md` prompts)
- [ ] **Visualize Status**: `/spec-kitty.status`

## Phase B: Review & Merge
- [ ] **Review Completed WPs**: `/spec-kitty.review`
- [ ] **Move to Review**: `python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE-SLUG> <WP> for_review`
- [ ] **Final Acceptance**: `/spec-kitty.accept`
- [ ] **Merge Feature**: `/spec-kitty.merge`


## See Also

- [[spec-kitty-meta-tasks]]
- [[spec-kitty-workflow]]
- [[spec-kitty-workflow]]
- [[dual-loop-meta-tasks]]
- [[learning-loop-meta-tasks]]
- [[identity-the-spec-kitty-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/spec-kitty-meta-tasks.md`
- **Indexed:** 2026-04-17T06:42:10.368031+00:00
