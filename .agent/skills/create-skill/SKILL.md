---
name: create-skill
accreditation: Patterns, examples, and terminology gratefully adapted from Anthropic public plugin-dev and skill-creator repositories.
description: >
  This skill should be used when the user wants to "create a skill", "add a skill",
  "write a new skill", "build a skill for my plugin", "scaffold a skill", "make a skill
  that does X", "improve skill description", "run evals on a skill", "benchmark skill
  performance", "optimize triggering", or needs guidance on skill structure, progressive
  disclosure, trigger descriptions, or skill development best practices. Use this skill
  even when the user just wants to improve an existing skill -- jump straight to the
  eval/iterate loop if a draft already exists. Do NOT use this for creating sub-agents
  (use create-sub-agent), slash commands (use create-command), or hooks
  (use create-hook).
disable-model-invocation: false
allowed-tools: Bash, Read, Write
---

# Skill Designer and Architect

Skills are modular packages that transform Claude from a general-purpose agent into a
specialist. Think of a skill as an "onboarding guide" for a specific domain -- it gives
Claude procedural knowledge, reusable resources, and triggering conditions that no base
model can fully possess.

**Start by figuring out where the user is in the process:**
- "I want to make a skill for X" -> start from Step 1 (capture intent)
- "I already have a skill, let's improve it" -> jump to Step 5 (eval + iterate)
- "Just help me, don't need evals" -> vibes mode: write, show, adjust based on feedback

Be flexible. The process is a guide, not a cage.

> All content references below use `${CLAUDE_PLUGIN_ROOT}` for portable paths.
> Read `references/hitl-interaction-design.md` and `references/pattern-decision-matrix.md`
> at the start if you need in-depth interaction design and L4 pattern guidance.

---

## Step 1: Understand the Skill with Concrete Examples

Start here. Do not ask abstract questions about skill design until the concrete use case
is clear. The concrete examples drive every downstream decision.

Review the conversation history for existing context before asking anything.
Ask only what is still unclear. Group related questions.

**Core questions:**

1. **What does this skill do?** What is the user trying to accomplish?

2. **What would a user say that should trigger this skill?** Ask for 3-5 real examples:
   - "What exact phrases would someone type to use this?"
   - "Can you give me an example of a task this skill should handle?"

3. **What reusable resources does this skill need?** For each concrete example, think:
   - Is there code that gets rewritten every time? -> `scripts/`
   - Is there reference documentation Claude needs to consult? -> `references/`
   - Are there template files or assets that get used in the output? -> `assets/`
   - Are there working code examples to learn from? -> `examples/`

4. **What is the input and output?** What does Claude receive, what does it produce?

5. **Are there edge cases or failure modes to handle?** What should happen when input is
   missing, malformed, or ambiguous?

Conclude Step 1 when there is a clear picture of the use cases, trigger phrases, and
what reusable resources are needed.

---

## Step 2: Plan the Skill Structure

Map the gathered information to the four-layer anatomy:

```
skill-name/
├── SKILL.md           (required -- always loaded when skill triggers)
├── references/        (optional -- loaded by Claude as needed)
│   ├── patterns.md
│   └── advanced.md
├── examples/          (optional -- working code to copy and adapt)
│   └── example.sh
├── scripts/           (optional -- deterministic utilities, run without loading into context)
│   └── validate.sh
└── assets/            (optional -- template files used IN the output, not documentation)
    └── template.html
```

**Decision rules:**

| Content Type | Where It Goes |
|-------------|---------------|
| Core workflow and overview | `SKILL.md` (keep lean: 1,500-2,000 words) |
| Detailed patterns, API docs, schemas | `references/` |
| Working runnable code examples | `examples/` |
| Validation/utility scripts | `scripts/` |
| Template files, boilerplate, icons, fonts | `assets/` |
| Code rewritten every time -> script it | `scripts/` |
| Documentation too large (>10k words) -> add grep patterns | `references/` with grep hints |

**Size target:** `SKILL.md` body should be 1,500-2,000 words. Over 3,000 words is a
sign that content should be moved to `references/`. The skill-reviewer agent will flag this.

**Domain variant organization:** When a skill supports multiple technologies or frameworks,
organize by variant in `references/` -- Claude reads only the relevant one:
```
cloud-deploy/
├── SKILL.md  (workflow + variant selector)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

**Script bundling signal:** After running test cases, look for repeated work. If multiple
eval runs all independently wrote the same helper script (e.g., `create_docx.py`,
`build_chart.py`), that is a strong signal to bundle that script in `scripts/` and tell
the skill to use it. Every future invocation benefits.

---

## Step 3: Recap and Confirm Before Scaffolding

Pause here. Present the plan before writing any files:

```
Skill Design:
  Name:          <kebab-case-name>
  Trigger desc:  "This skill should be used when [specific phrases]..."
  Resources:
    references/: [file list and purpose]
    examples/:   [file list and purpose]
    scripts/:    [file list and purpose]
    assets/:     [file list and purpose]

  SKILL.md outline:
    - [Section 1]
    - [Section 2]
    - References to above files

Does this look right? (yes / adjust)
```

Do NOT scaffold until the user confirms.

---

## Step 4: Build the Skill

### 4a. Scaffold the Directory

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py \
  --type skill \
  --name <skill-name> \
  --path <destination-directory> \
  --desc "<short description>"
```

Delete any scaffold directories not needed. Create only what the plan requires.

If iterating on an existing skill, do NOT overwrite immediately. Write to
`/tmp/skill-preview/<name>/` first for complex changes.

### 4b. Create Reusable Resources First

Start with `references/`, `scripts/`, `assets/`, and `examples/` BEFORE writing `SKILL.md`.
This order prevents SKILL.md from bloating -- once the resources exist, SKILL.md becomes
lean pointer + core flow.

For each resource file:
- `references/` files: Documentation that Claude reads while working. Keep factual, dense.
- `scripts/` files: Make executable (`chmod +x`). Add usage comment at top.
- `assets/` files: Template or boilerplate content. Document in SKILL.md how to use them.
- `examples/` files: Complete, runnable examples. Label inputs and expected outputs.

If the user needs to provide content (brand assets, company schemas, API docs), ask now.

### 4c. Write SKILL.md

**Writing style rules (enforce strictly):**

```
CORRECT (imperative/infinitive form):
  "Start by reading the config file."
  "Validate input before processing."
  "Use the grep tool to search for patterns."

WRONG (second person -- do not use):
  "You should start by reading the config file."
  "You need to validate input."
  "You can use grep to search."
```

**Body structure (every SKILL.md should cover):**
1. Brief purpose statement (2-3 sentences max)
2. Core workflow / step-by-step process
3. Quick reference tables or key constraints
4. Explicit pointers to `references/`, `examples/`, `scripts/` with what each contains

**Description (frontmatter) requirements:**
- Third-person format: `"This skill should be used when the user asks to "X", "Y", "Z"..."`
- Include 3-5 exact trigger phrases in quotes
- Be specific -- vague descriptions cause under-triggering
- **Make the description a little "pushy"** to combat Claude's known tendency to undertrigger.
  Instead of a passive statement, add a nudge: "Make sure to use this skill whenever the user
  mentions X, even if they don't explicitly ask for it."

```yaml
# CORRECT (with anti-undertrigger nudge):
description: >
  This skill should be used when the user asks to "create a hook",
  "add a PreToolUse hook", "validate tool use", or mentions hook events
  (PreToolUse, PostToolUse, Stop). Use this skill whenever hooks are mentioned
  even if the user doesn't use the word "hook" explicitly.

# WRONG:
description: Provides guidance for working with hooks.  # vague, not third-person
```

**Triggering mechanics note:** Skills only trigger on substantive, multi-step queries.
Simple one-step requests ("read this file") won't trigger skills regardless of description
quality. Eval queries should be realistic and detailed -- include file paths, personal
context, company names. Avoid abstract requests like "Extract text from PDF";
prefer: "my boss just sent me a PDF report and I need to pull the financial tables out
into a spreadsheet." Near-miss negative queries are the most valuable test cases.

**Add evals and acceptance criteria:**

Save test cases to `evals/evals.json` -- prompts only, no assertions yet:
```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt (be realistic and specific -- not abstract)",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```
Create iteration ledger: `evals/results.tsv`
Header: `iteration\ttrain_score\ttest_score\tdecision\tnotes\tdescription`

For skills with L4 patterns (dual-mode bootstrap, artifact lifecycle, etc.), read the
pattern decision matrix first:
- Read `references/hitl-interaction-design.md`
- Read `references/pattern-decision-matrix.md`
- Embed only the pattern-specific scaffolding needed; link detailed docs to `references/`

---

## Step 5: Validate and Iterate

### Quality Gate: skill-reviewer

After generating the skill, trigger the skill-reviewer quality check:
```
"Review my skill and check if it follows best practices"
```

The skill-reviewer checks: description quality, trigger phrases, imperative writing style,
progressive disclosure (lean SKILL.md, detailed content in references/), and broken references.

### Running Evals (with-skill vs baseline parallel)

For each test case, spawn two subagents **in the same turn** -- one with the skill, one
without. Do not run with-skill first and come back for baseline later:

**With-skill run:**
```
Task: <eval prompt>
Skill path: <path-to-skill>
Save outputs to: <skill-name>-workspace/iteration-<N>/eval-<ID>/with_skill/outputs/
```

**Baseline run:**
- New skill: no skill at all (same prompt, `without_skill/outputs/`)
- Improving existing: snapshot first (`cp -r <skill> workspace/skill-snapshot/`), then use snapshot

While runs execute, draft assertions in parallel. Good assertions are objectively verifiable
with descriptive names. After runs complete, capture timing from task notification:
```json
{ "total_tokens": 84852, "duration_ms": 23332 }
```
Save to `timing.json` immediately -- this data is only available via task notification.

### Trigger Optimization

Run the description optimization loop (splits 60% train / 40% test, 5 iterations max):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/benchmarking/run_loop.py \
  --skill-path <skill-path> \
  --eval-set evals/evals.json \
  --model <model> \
  --results-dir evals/experiments
```

Visualize:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/eval-viewer/generate_review.py <eval-output-dir>
```

**Description quality checklist:**
- [ ] Opens with third-person: "This skill should be used when..."
- [ ] Contains 3-5 trigger phrases in quotes (what a user would actually say)
- [ ] Has anti-undertrigger nudge: "Use this even when user doesn't explicitly say..."
- [ ] Precise action verbs: `"scaffold"` not `"help"`, `"audit"` not `"check"`
- [ ] Includes at least 1 negative boundary: "Do NOT use this for..."
- [ ] Under 100 words in the metadata field

**SKILL.md content checklist:**
- [ ] Body in imperative/infinitive form (no "You should...")
- [ ] 1,500-2,000 words (lean); over 3,000 = move content to `references/`
- [ ] All referenced files actually exist
- [ ] Instructions explain the *why* -- avoid excessive ALWAYS/NEVER/MUST capitalizations
- [ ] `references/`, `examples/`, `scripts/`, `assets/` directories documented with contents

### Iteration and Writing Philosophy

When improving after eval feedback:
1. **Generalize** from the specific examples -- the skill runs millions of times, not just on these test cases
2. **Explain the why** -- today's LLMs have good theory of mind. Explain reasoning instead of rigid MUSTs. "ALWAYS do X" is a yellow flag; try reframing to explain why X matters
3. **Keep it lean** -- remove instructions that aren't pulling their weight. Read transcripts to find where the skill made the model do unproductive work and trim those instructions
4. **Bundle repeated work** -- if multiple eval runs all wrote the same helper script, put it in `scripts/` once
5. Strengthen trigger phrases if skill under-triggered
6. Move long sections to `references/` if body is bloated

---

## Next Actions
- **Quality review**: Trigger `skill-reviewer` agent to audit description and content
- **Continuous improvement**: Run `./scripts/benchmarking/run_loop.py` for trigger optimization
- **Audit**: Run `audit-plugin` to validate the full plugin structure
- **Convert to agent**: Run `create-agentic-workflow` for a GitHub-native version

---

## Reference Files

Read these when needed:
- `references/hitl-interaction-design.md` - Interaction modes (autonomous, guided, hybrid)
- `references/pattern-decision-matrix.md` - L4 pattern routing (artifact lifecycle, dual-mode, etc.)
- `references/patterns/` - Individual L4 pattern definitions (load only when pattern is triggered)
- `references/acceptance-criteria.md` - How to write testable acceptance criteria
