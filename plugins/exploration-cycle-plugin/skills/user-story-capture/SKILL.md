---
name: user-story-capture
description: >
  Derives, groups, and refines user stories from exploration work, prototype behavior,
  and business context, with prioritization for the first implementation slice.
  Supports standard "As a / I want / So that" format and Gherkin "Given / When / Then"
  Acceptance Criteria format. Trigger with "generate user stories", "write acceptance criteria",
  "create Gherkin scenarios", "derive stories from requirements", or "create a backlog".
allowed-tools: Bash, Read, Write
---

# User Story Capture

Derive structured user stories and acceptance criteria from exploration session captures.

## Usage

```bash
python ./scripts/execute.py \
  --input <file> [<file2>...] \
  --format <standard|gherkin> \
  --output <output_file.md>
```

**Formats:**
- `standard` *(default)*: `As a [user type], I want [goal], so that [benefit]` — with priority table and gaps.
- `gherkin`: Standard + `Given / When / Then` Acceptance Criteria blocks per story.

**Flags:**
- `--input PATH [PATH ...]` : Session brief, BRD draft, prototype notes, or prior captures
- `--output PATH` : Destination file (default: `exploration/captures/user-stories-draft.md`)
- `--format FORMAT` : Output format (default: `standard`)

## Interactive Co-Authoring Workflow

When invoked interactively, follow this 3-stage pattern. Do not dump a full story list at once.

### Stage 1: Context Gathering
Ask all three questions in a single message before generating anything:

1. **Input files:** Which source documents should I work from? (Check `exploration/` — list what you find: session brief, BRD draft, prototype notes.) If no files exist, stop and ask for input before proceeding.
2. **Primary actor:** Which user role, system actor, or job-to-be-done is the highest priority for the first implementation slice? (Use role-neutral language — e.g., "the person approving requests", "the agent running evals", not just "the user".)
3. **Out-of-scope:** Are there any actors or workflows we should explicitly exclude from this story set?
4. **Format:** Should acceptance criteria use standard format (`As a / I want / So that`) or Gherkin (`Given / When / Then`)? Default to standard unless Gherkin is requested.

After the user responds: read each input file they identify.

### Stage 2: Iterative Refinement
Build the backlog in layers — do not jump straight to full Gherkin blocks.

1. **Outline first:** Based on the input files and primary actor, present a numbered list of lightweight story titles (one line each, no ACs yet). Ask: *"Which of these should we keep, cut, or merge for the first slice?"*
2. **Curate:** Apply changes. Mark any story derived from unclear or inferred source material as `[UNCONFIRMED]`.
3. **Draft approved stories:** For each kept story, write the full format:
   - Standard: `As a [actor], I want [goal], so that [benefit].`
   - Gherkin: Add `Given / When / Then` AC blocks after the story statement.

   **Gherkin format rules:**
   - `Given` = precondition or system state before the action (what is already true)
   - `When` = the single action or event the actor performs
   - `Then` = the observable, testable outcome (what changes or appears)
   - One `When` per scenario. Use `And` for additional `Given` or `Then` clauses.

   Present each story and ask: *"Accurate? Anything to add or change?"* Apply edits before the next story.

### Stage 3: Reader Testing (Test-Driven ACs)
After all approved stories are drafted:

1. For each priority story (top 3 if there are many), predict exactly 2 edge cases or failure modes that a QA engineer would test but that the current ACs do not cover. An edge case must be specific and testable — not generic ("what if it fails?") but concrete ("what if the file is missing at sync time?").
2. Present the gaps: *"Story [N] doesn't handle: [edge case 1], [edge case 2]. Should we add scenarios for these?"*
3. If yes: add `Given / When / Then` blocks for the confirmed edge cases. Mark inferred edge cases `[UNCONFIRMED]` until the user confirms they are real scenarios.
4. Collect all unresolved questions in a `## Story Gaps` section at the end.

## Anti-Hallucination Rules

- Do NOT invent user types, goals, or benefits not described in source captures.
- Do NOT fabricate edge cases in Gherkin AC without evidence from input files or explicit user confirmation.
- Mark inferred stories and scenarios `[UNCONFIRMED]` — only promote to `[CONFIRMED]` after human sign-off.
- Do NOT proceed without input files — stories generated from nothing are pure hallucination.
- **Source citations required:** each story must note which input file it derives from (e.g., `(source: brd-draft.md, Functional Requirements)`). Stories with no traceable source must be marked `[UNCONFIRMED — inferred, not in source]`.
- **`## Story Gaps` section is mandatory** — list every open decision or missing actor definition exactly once.

<example>
Context: BRD draft is complete, user wants a core story set.
user: "Generate user stories from our BRD."
assistant: "I'll run `user-story-capture` in standard format to derive a prioritised story set."
</example>

<example>
Context: User wants stories with ready-to-use Acceptance Criteria.
user: "Create Gherkin acceptance criteria for these requirements."
assistant: "I'll run `user-story-capture --format gherkin` to produce stories with Given/When/Then AC blocks."
</example>

<example>
Context: Pre-sprint refinement.
user: "Write acceptance criteria for the checkout flow stories."
assistant: "I'll use `user-story-capture --format gherkin` with the checkout BRD sections as input."
</example>
