# Acceptance Criteria: capturing-business-requirements

## 1. Routing
- [ ] Triggers on "capture requirements", "generate a BRD", "document the business rules", "write user stories", "Gherkin acceptance criteria", "map this process".
- [ ] Does not trigger for architecture specs, engineering plans or implementation tasks.

## 2. Grounding
- [ ] Every requirement, rule and story traces to a source capture or to the expert's own words; nothing is invented.
- [ ] Explicit statements are `[CONFIRMED]`, inferences are `[UNCONFIRMED]`, and no marker is promoted without SME sign-off.
- [ ] Every story cites its source file, for example `(source: brd-draft.md)`.

## 3. Gap handling
- [ ] The gap marker is the exact string `[NEEDS HUMAN INPUT]` with any reason in parentheses after it; variants are never written.
- [ ] Each open decision appears once under `## Consolidated Gaps`; stories add a `## Story Gaps` section.
- [ ] `Decision Pre-fills` from the brief are treated as confirmed and never re-marked as gaps.
- [ ] `python3 ../running-exploration-cycle/scripts/check_gaps.py --files <captures> --threshold 3` exits 0 before captures are handed on.

## 3b. Outputs
- [ ] `python3 scripts/business_requirements_capture_execute.py --input <file> --mode brd --output <file>` writes a BRD skeleton with the standard sections and a DRAFT status line.
- [ ] `python3 scripts/user_story_capture_execute.py --input <file> --format gherkin --output <file>` writes stories with one `When` clause per scenario.
- [ ] `python3 scripts/generate_workflow.py --input <file> --output <file> --type flowchart` writes a fenced Mermaid block marked DRAFT with an `## Open Questions` section.

## 4. Roles
- [ ] `prototype-notes.md` has a single writer, the observation-extraction template; it contains no `[NEEDS HUMAN INPUT]` (items needing confirmation use `[UNCONFIRMED]` with a reason).
- [ ] Each invocation runs exactly one capture mode; a missing `Mode:` stops with an error.
- [ ] No model IDs or prices are named in prompts or docs.
