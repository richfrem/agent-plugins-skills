# Copilot Sonnet Orchestration Brief
**For:** Fresh Antigravity session (Claude Sonnet 4.6 Thinking)
**Date written:** 2026-04-06
**Cost model:** Copilot charges per REQUEST not per token.
**Strategy:** ONE single Copilot request generates ALL file content. Antigravity writes files, cleans up, and commits.

---

## Your Mission

You are a **Meta-Harness Orchestrator**. You dispatch ONE comprehensive Copilot CLI request
that generates all missing file content in a single shot. You then use your own file tools
to write every file, do the cleanup, and commit. You document learnings for the
`superpowers-analysis.md`.

**Copilot is used exactly ONCE.** All file writes, deletes, and git operations are done by
you (Antigravity) using your native tools. Do NOT make follow-up Copilot requests unless
the first one is critically incomplete (missing a whole file, not just minor edits).

---

## Repositories & Key Paths

| Item | Path |
|---|---|
| Plugin working dir | `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/exploration-cycle-plugin/` |
| Full execution plan | `[plugin dir]/docs/superpowers/plans/2026-04-06-gap-fill-cleanup-attribution.md` |
| Copilot CLI skill | `/Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/SKILL.md` |
| superpowers analysis | `/Users/richardfremmerlid/Projects/AI-Research/01-Research/harnesses/superpowers/superpowers-analysis.md` |
| Opp 3 design plan | `/Users/richardfremmerlid/Projects/AI-Research/07-Opportunities/03-Exploration-and-Design/exploration-cycle-plugin-design-plan.md` |

---

## Step 0: Mandatory Pre-Flight (Before Any Copilot Call)

Read these files using your file tools (NOT shell commands):
1. Read the full plan: `[plugin dir]/docs/superpowers/plans/2026-04-06-gap-fill-cleanup-attribution.md`
2. Read the Copilot CLI skill: `/Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/SKILL.md`
3. Verify what files currently exist in `[plugin dir]/skills/` using `list_dir` tool

Then run the heartbeat check:
```bash
python3 /Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null /tmp/heartbeat.md \
  "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."
```
Verify `/tmp/heartbeat.md` contains `HEARTBEAT_OK` before proceeding.

---

## Step 1: THE ONE COPILOT REQUEST

Build a single prompt that generates ALL missing file content at once.
Write the prompt to a temp file first (avoids shell escaping issues):

```bash
cat > /tmp/copilot_prompt.md << 'PROMPT_EOF'
You are a senior agent skill author. Your task is to generate the complete file content
for 4 new/updated agent skill files. Output ALL files in one response, separated by
clearly marked headers so they can be parsed and written individually.

Use this exact output format for each file:

===FILE: [relative path from plugin root]===
[complete file content]
===ENDFILE===

---

## Context: What these skills are for

This is the `exploration-cycle-plugin` — an agentic plugin that guides non-technical
Subject Matter Experts (SMEs) through a structured discovery and prototyping workflow.
The plugin follows the GenAI Double Diamond framework. SME = business person, not a developer.

The plugin uses a HARD-GATE pattern from obra/superpowers (MIT license):
no prototype can be built until the SME approves a Discovery Plan.

Key persona rules for ALL skill content:
- Never use developer jargon: scaffold, repo, branch, commit, worktree, invoke, dispatch,
  iterate, initialize, spin up, phase, gate, spec, schema, subagent, context, tokens
- Use business language: "let me save that", "I'll take a note", "we'll build this together",
  "here's what I heard — does this look right?"
- Always confirm back to the SME in plain language before moving forward
- Ask ONE question at a time

---

## File 1: skills/discovery-planning/SKILL.md

YAML frontmatter (exactly):
```yaml
---
# Architectural patterns adapted from obra/superpowers (MIT)
# https://github.com/obra/superpowers
name: discovery-planning
description: >
  Guides an SME through a structured discovery session to produce an approved
  Discovery Plan before any prototype is built. Enforces the HARD-GATE: no prototype
  can be built until the SME has approved the plan. Trigger with "start a discovery
  session", "let's plan this out", "help me figure out what we're building",
  "I have an idea I want to explore", or "let's start from scratch".
allowed-tools: Read, Write
---
```

Required sections in the skill body:

1. Examples block (use <example> tags): 3 examples showing correct trigger → response

2. HARD-GATE Rule (displayed prominently):
   - DO NOT write any prototype files or hand off to prototype-builder until the SME
     explicitly approves the Discovery Plan with YES or equivalent affirmation
   - If the SME asks to "just build it" before approving: politely decline and complete
     the planning session first

3. Pre-Phase 0 (Silent Discovery — run before speaking to SME):
   - Check if `exploration/session-brief.md` exists (read for context if yes)
   - Create `exploration/discovery-plans/` directory if it doesn't exist
   - Do this silently — do not announce it to the SME

4. Discovery Session (5 required questions, one at a time):
   - Q1: What problem are we trying to solve for the people we serve?
   - Q2: Who are the people involved — who uses this, who approves, who is affected?
   - Q3: What does success look like when this is working well?
   - Q4: What are the must-haves vs. nice-to-haves?
   - Q5: Are there any hard rules, limits, or things we definitely cannot do?
   - After EACH answer: confirm back in 1-2 plain-language sentences. Ask clarifying
     questions if needed before moving to the next question.

5. Discovery Plan output format (write to `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`):
   ```markdown
   # Discovery Plan — [Date]
   ## Problem Statement
   ## Stakeholders
   ## Success Criteria
   ## Must-Have Requirements
   ## Constraints and Rules
   ## Open Questions
   ```

6. HARD-GATE Approval Gate:
   Present the completed plan to the SME with this exact message:
   > "Here is the plan we built together. Please read through it.
   > When you're happy with everything, reply **YES** to confirm it —
   > then we'll move on to the next stage. If anything needs adjusting, just tell me."
   Wait for YES. Do not write the file or proceed until received.

7. On approval: write the plan file. Announce:
   > "Your plan is saved. We're ready to move to the next stage."

---

## File 2: skills/discovery-planning/evals/evals.json

Standard evals JSON for 4 trigger phrases. Format:
```json
{
  "skill": "discovery-planning",
  "evals": [
    { "id": "eval-001", "trigger": "...", "expected_skill": "discovery-planning", "notes": "..." },
    ...
  ]
}
```
Triggers: "start a discovery session", "let's plan this out before building",
"I have an idea I want to explore", "help me figure out what we're building"

---

## File 3: skills/visual-companion/SKILL.md

YAML frontmatter:
```yaml
---
name: visual-companion
description: >
  Presents layout direction options to the SME before prototype construction begins.
  Invoked by prototype-builder-agent after Discovery Plan approval to confirm the
  visual structure before building starts. Trigger with "what should it look like",
  "show me some layout options", "let me see the design options", or when dispatched
  by prototype-builder-agent for layout confirmation.
allowed-tools: Read, Write
---
```

Required sections:

1. Examples block: 2 examples

2. Session flow:
   - Step 1: Read the approved Discovery Plan from `exploration/discovery-plans/`
     (most recent file). Understand the problem before proposing anything.
   - Step 2: Present 3 layout options adapted to the Discovery Plan context.
     Describe each in plain language (2-3 sentences each, no technical terms).
     Label them Option A, Option B, Option C.
     Generic examples to adapt: (A) single-page dashboard with summary + detail,
     (B) step-by-step wizard one thing at a time, (C) split-screen list + detail panel
   - Step 3: Ask: "Which of these feels closest to what you had in mind?
     Or describe something different and I'll work with that."
   - Step 4: Write the confirmed choice to `exploration/captures/layout-direction.md`
   - Step 5: Announce layout is confirmed, ready for building to begin

---

## File 4: skills/visual-companion/evals/evals.json

3 trigger evals. Triggers: "what should it look like",
"show me some layout options", "let me see the design options before we build"

---

## File 5: skills/subagent-driven-prototyping/SKILL.md

YAML frontmatter:
```yaml
---
# Architectural patterns adapted from obra/superpowers (MIT)
# https://github.com/obra/superpowers
name: subagent-driven-prototyping
description: >
  Builds an interactive prototype component-by-component, reviewing each piece
  before moving to the next. Requires an approved Discovery Plan and confirmed
  layout direction before starting. Trigger with "build the prototype",
  "let's build it", "start building", or when dispatched by prototype-builder-agent
  after visual-companion confirms layout direction.
allowed-tools: Bash, Read, Write
---
```

Required sections:

1. Examples block: 2 examples

2. Required inputs check (stop if either missing):
   - Discovery Plan: `exploration/discovery-plans/` (most recent)
   - Layout Direction: `exploration/captures/layout-direction.md`
   If missing: report which file is missing and stop.

3. Component decomposition:
   - Based on Discovery Plan + layout, identify 3-5 prototype components
   - Announce to the user (business language):
     > "I'll put this together in [N] parts. I'll check each one before moving to
     > the next to make sure everything matches your plan."

4. Build loop (per component):
   - Announce: "Working on: [plain-language component name]..."
   - Write component to `exploration/prototype/components/[name].[ext]`
   - Self-review: check the component against the Discovery Plan requirements
   - Status must be one of: COMPLETE | BLOCKED | NEEDS_CONTEXT
   - If BLOCKED or NEEDS_CONTEXT: stop, explain in plain language, ask for clarification
   - Do NOT proceed to next component until current is COMPLETE

5. Assembly phase (after all components COMPLETE):
   - Assemble `exploration/prototype/index.html` (or equivalent entry point)
   - Write `exploration/prototype/README.md` with plain-language run instructions
     (e.g., "Open index.html in your browser" — no technical setup instructions)

6. Completion report to prototype-builder-agent:
   - All components built and assembled
   - Entry point location
   - Ready for SME walkthrough

7. Persona enforcement (call out explicitly):
   - Say "build" not "scaffold"
   - Say "set up" not "initialize"
   - Say "put together" not "spin up"
   - Progress updates: brief, clear, business-friendly

---

## File 6: skills/subagent-driven-prototyping/evals/evals.json

3 evals. Triggers: "build the prototype now", "let's build it",
"start building the prototype"

---

## File 7: skills/prototype-builder/SKILL.md

This REPLACES the current stub completely. The current file contains only:
"> ⚠️ STUB — execute.py not yet implemented."
That entire file must be replaced.

YAML frontmatter:
```yaml
---
name: prototype-builder
description: >
  Orchestrates the full prototype build: reads the approved Discovery Plan,
  confirms layout direction via visual-companion, then drives the component-by-component
  build. HARD-GATE enforced: no build starts without an approved Discovery Plan.
  Trigger with "build a prototype", "create a working prototype",
  "show me a working version", or "prototype to clarify scope".
allowed-tools: Bash, Read, Write
---
```

Required sections:

1. Examples block: 2 examples

2. HARD-GATE Check (first thing, before anything else):
   Check if `exploration/discovery-plans/` exists and contains at least one plan file.
   If no plan exists:
   > "Before we can build, I need to understand what we're building first.
   > Can we start with a planning session?"
   Do NOT continue without a plan.

3. Session flow:
   - Step 1: Read the most recent Discovery Plan
   - Step 2: Invoke visual-companion skill for layout direction
   - Step 3: Invoke subagent-driven-prototyping skill for component-by-component build
   - Step 4: Guide SME walkthrough — ask them to click through each main flow
   - Step 5: Write observations to `exploration/captures/prototype-notes.md`
     (confirmed flows, surprises, new rules observed, edge cases raised)
   - Step 6: Hand off to prototype-companion-agent for structured requirement extraction
     Announce: "I'll pass your walkthrough notes to the next stage now."

4. This skill coordinates — it does NOT build components directly.
   All building is done by subagent-driven-prototyping.

PROMPT_EOF
```

Now dispatch to Copilot:
```bash
copilot -p "$(cat /tmp/copilot_prompt.md)" > /tmp/copilot_output.md
```

Then verify output exists and is substantial:
```bash
wc -l /tmp/copilot_output.md
```
Expected: 200+ lines. If less than 50 lines, the request likely failed — check for error messages.

---

## Step 2: Parse and Write Files (You Do This — Not Copilot)

Read `/tmp/copilot_output.md` using your file tools. Parse out each
`===FILE: [path]===` ... `===ENDFILE===` block and write each file
using your `write_to_file` tool to:

```
[plugin dir]/skills/discovery-planning/SKILL.md
[plugin dir]/skills/discovery-planning/evals/evals.json
[plugin dir]/skills/visual-companion/SKILL.md
[plugin dir]/skills/visual-companion/evals/evals.json
[plugin dir]/skills/subagent-driven-prototyping/SKILL.md
[plugin dir]/skills/subagent-driven-prototyping/evals/evals.json
[plugin dir]/skills/prototype-builder/SKILL.md
```

After writing each file, verify it was written correctly by reading it back.

---

## Step 3: Clean Up `skills/deferred/` (You Do This — No Copilot Needed)

Delete these using your file tools or a single targeted shell command:

Files to remove:
- `skills/deferred/exploration-cycle-orchestrator-agent.md` (52-byte stub)
- `skills/deferred/prototype-companion-agent.md` (41-byte stub)
- `skills/deferred/exploration-orchestrator/` (whole dir — promoted to active)
- `skills/deferred/prototype-builder/` (whole dir — promoted to active)

Keep:
- `skills/deferred/SKILL.md` — update it to remove references to the two now-promoted skills
- `skills/deferred/evals/` — keep
- `skills/deferred/agents/` — keep if non-empty
- `skills/deferred/references/` — keep if non-empty

---

## Step 4: Update README.md (You Do This — No Copilot Needed)

Add two sections to `README.md`:

### 4a — Updated directory structure map
Replace the `### Directory Structure` code block with the updated version showing all 3
new skills and marking them `# NEW: post-SMR`.

### 4b — Attribution block
Add a new `## 📜 Attribution & License` section at the bottom with:

```markdown
---

## 📜 Attribution & License

### Architectural Inspiration: `obra/superpowers`

The `exploration-cycle-plugin` borrows core architectural patterns from
[**obra/superpowers**](https://github.com/obra/superpowers), an open-source
agentic harness by Jesse Vincent (obra).

Patterns adapted:

| Pattern | Source | Adapted As |
|---|---|---|
| `<HARD-GATE>` execution block | `brainstorming` skill | `discovery-planning` skill |
| Blank-slate context isolation per task | Execution harness | `subagent-driven-prototyping` skill |
| Two-stage verification (Spec + Quality) | Verification layer | Business Rule Audit + Prototype Walkthrough |
| Linguistic Detox (persona scan) | Jargon policing | SME language enforcement across all agents |
| Manifest-Driven Scaffolding | Pre-flight scaffolding | Pre-Phase 0 Silent Discovery |

**superpowers is licensed under the MIT License.**
Full text: https://github.com/obra/superpowers/blob/main/LICENSE

The `exploration-cycle-plugin` is independently authored and not affiliated with or endorsed by obra/superpowers.
```

---

## Step 5: Commit and Push

```bash
cd /Users/richardfremmerlid/Projects/agent-plugins-skills

git add plugins/exploration-cycle-plugin/skills/discovery-planning/
git add plugins/exploration-cycle-plugin/skills/visual-companion/
git add plugins/exploration-cycle-plugin/skills/subagent-driven-prototyping/
git add plugins/exploration-cycle-plugin/skills/prototype-builder/SKILL.md
git add plugins/exploration-cycle-plugin/README.md
git add plugins/exploration-cycle-plugin/skills/deferred/SKILL.md

git commit -m "feat: fill SMR gap skills, clean deferred/, add superpowers attribution

- Add discovery-planning skill (HARD-GATE brainstorming, SME-led)
- Add visual-companion skill (layout direction before build)
- Add subagent-driven-prototyping skill (component-by-component build)
- Replace prototype-builder SKILL.md stub with full orchestration skill
- Remove orphaned stubs from skills/deferred/ (promoted to active)
- Add obra/superpowers attribution and MIT license to README

Architectural patterns adapted from https://github.com/obra/superpowers (MIT)"

git push
```

---

## Verification (File Tools Only — No Shell Grep)

Read each of these files to confirm correct content:
- [ ] `skills/discovery-planning/SKILL.md` — contains "HARD-GATE" and "YES"
- [ ] `skills/discovery-planning/evals/evals.json` — valid JSON
- [ ] `skills/visual-companion/SKILL.md` — contains "layout-direction.md"
- [ ] `skills/subagent-driven-prototyping/SKILL.md` — contains "BLOCKED" and "NEEDS_CONTEXT"
- [ ] `skills/prototype-builder/SKILL.md` — does NOT contain "STUB"
- [ ] `README.md` — contains "obra/superpowers"

---

## Learnings to Document in `superpowers-analysis.md`

Add new observations for anything interesting you see, such as:
- Did Copilot follow the structured output format (`===FILE:===` delimiters) reliably?
- Did it produce SME-friendly language or did it leak dev jargon that needed cleanup?
- Did 1 request cover all 7 files adequately, or were gaps significant?
- What is the minimum viable prompt structure for reliable multi-file generation?

Add as Observation #36+ to `superpowers-analysis.md`.

---

## What NOT to Do

- ❌ Do NOT run shell `grep` or `find` against `agent-plugins-skills` — use file reading tools
- ❌ Do NOT background (`&`) the Copilot call
- ❌ Do NOT make a second Copilot request unless the first produced < 50 lines
- ❌ Do NOT skip the heartbeat check
- ❌ Do NOT let Copilot write files directly — you parse output and write with your tools

---

*Written by Antigravity (session ad60116f). Restart-safe handoff document.*
*One Copilot request. All file writes done by Antigravity.*
