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
