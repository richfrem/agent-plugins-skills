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
python3 ${CLAUDE_PLUGIN_ROOT}/skills/user-story-capture/scripts/execute.py \
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

When invoked interactively by a user, do not just run the batch command blindly. Follow this 3-stage co-authoring pattern to ensure high quality:

### Stage 1: Context Gathering
Before generating the stories, ask the user:
1. Which persona or user journey is the highest priority for the first implementation slice?
2. Are there any out-of-scope personas we should explicitly ignore?
*(If the user says "just generate it", proceed immediately).*

### Stage 2: Iterative Refinement
Instead of jumping straight to heavy Gherkin blocks, build the backlog interactively:
1. **Outline First:** Brainstorm and present a numbered list of lightweight story titles (no ACs yet).
2. **Curate:** Ask the user which stories to keep, cut, or merge for the first slice.
3. **Draft:** Run the `execute.py` script to generate the full formatting (including Gherkin ACs if requested) only for the approved stories.

### Stage 3: Reader Testing (Test-Driven ACs)
To ensure the Acceptance Criteria are robust:
1. Predict 2-3 edge cases or failure modes for each priority story.
2. Verify that the generated Given/When/Then blocks explicitly handle those edge cases. If they don't, surface the gaps to the user and iterate on the ACs.

## Anti-Hallucination Rules

- Do NOT invent user types, goals, or benefits not described in the source captures.
- Do NOT fabricate edge case scenarios in Gherkin AC without source evidence.
- Mark inferred stories as `[UNCONFIRMED]` — only mark `[CONFIRMED]` after human sign-off.
- Consolidate unresolved questions into a `## Story Gaps` section.

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
