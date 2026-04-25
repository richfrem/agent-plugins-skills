# Copilot Delegation — os-architect Tester + os-evolution-planner
# Task: 0019 (Round 2) | Model: claude-sonnet-4.6 | Date: 2026-04-25

You are adding two new artifacts to `plugins/agent-agentic-os/` in the
`agent-plugins-skills` monorepo. All paths are relative to the repo root.
Use the Write tool to write files directly — do not output delimiters.

Context: `os-architect-agent.md` was created in round 1. WS-G adds a tester agent
that validates it via pre-scripted scenario transcripts. WS-H adds a reusable skill
that codifies the plan+prompt+dispatch workflow used to build tasks 0018 and 0019.

---

## Workstream G — Create `plugins/agent-agentic-os/agents/os-architect-tester-agent.md`

This is a non-interactive CLI sub-agent. It runs a pre-scripted conversation through
os-architect (via Copilot CLI) and evaluates the output against acceptance criteria.
Write it in second-person ("You are...").

### Frontmatter

```yaml
---
name: os-architect-tester
description: >
  Validation agent for os-architect. Runs pre-scripted user scenarios through the
  os-architect interview flow via Copilot CLI, evaluates whether classification,
  routing, and HANDOFF_BLOCK output meet acceptance criteria, and produces a structured
  test report. Use to battle-harden os-architect after changes, or to validate a new
  version before deploying to .agents/.
  <example>
  user: "test os-architect with the pattern-abstraction scenario"
  assistant: [os-architect-tester-agent dispatches the scenario to Copilot CLI, evaluates the transcript, produces pass/fail test report]
  </example>
  <example>
  user: "run all 3 built-in scenarios against os-architect"
  assistant: [os-architect-tester-agent runs pattern-abstraction, gap-fill, and lab-setup scenarios in sequence, produces consolidated test report]
  </example>
model: inherit
color: orange
tools: ["Bash", "Read", "Write"]
---
```

### Body

Write the following sections in order.

#### Section 1: Identity

```markdown
## Identity

You are os-architect-tester — a validation agent that battle-hardens os-architect by
running pre-scripted user scenarios through it via Copilot CLI and evaluating whether
the outputs meet the published acceptance criteria.

You do NOT interact with os-architect interactively. You format a scenario as a
single-shot Copilot CLI prompt (system prompt + simulated conversation transcript),
dispatch it, then evaluate the response.
```

#### Section 2: Acceptance Criteria

Under `## Acceptance Criteria`, write these 4 criteria — these are what every scenario is evaluated against:

```markdown
## Acceptance Criteria

These criteria apply to every scenario run. Each must pass for a scenario to be marked PASS.

| # | Criterion | Pass Condition |
|---|-----------|----------------|
| AC-1 | Intent classified correctly | Correct category (1–5) stated within 2 turns |
| AC-2 | Dispatch strategy gated | Strategy not stated before tools question (Phase 1 Q2) is answered |
| AC-3 | Path C evals HARD-GATE | If gap-fill scenario: agent states evals review required before loop runs |
| AC-4 | Audit verification cited | Agent references file-read or memory source before claiming match/gap |
```

#### Section 3: Built-in Scenario Library

Under `## Built-in Scenario Library`, write 3 scenarios. Each scenario includes:
- `id`: slug
- `category`: expected intent category (number + label)
- `expected_path`: A, B, or C
- `user_turns`: list of pre-scripted user messages (in order)
- `evaluation_notes`: what to look for in the response

```markdown
## Built-in Scenario Library

### Scenario: pattern-abstraction
- **Category expected**: 1 — Pattern Abstraction
- **Path expected**: A or B
- **User turns**:
  1. "I found a new browser automation approach I want to apply to my agent skills"
  2. "The target would be os-eval-runner and exploration-workflow"
  3. "I have GitHub Copilot CLI available"
  4. "Success means those skills have the browser automation pattern embedded"
- **Evaluate for**: AC-1 (Category 1 within 2 turns), AC-2 (dispatch not set until turn 3), AC-4 (audit cites memory or file)

### Scenario: gap-fill
- **Category expected**: 4 — Capability Gap Fill
- **Path expected**: C
- **User turns**:
  1. "I need an agent that monitors plugin health automatically — checks for stale evals, broken symlinks, and missing Gotchas sections. It doesn't exist yet."
  2. "There's nothing like this in the current ecosystem"
  3. "I have Copilot CLI available"
  4. "Success means I can invoke it and get a health report"
- **Evaluate for**: AC-1 (Category 4 within 2 turns), AC-2 (dispatch gated), AC-3 (evals HARD-GATE mentioned before loop), AC-4 (audit cites "none" match with verification)

### Scenario: lab-setup
- **Category expected**: 3 — Lab Setup / Improvement Loop
- **Path expected**: A (route to improvement-intake-agent)
- **User turns**:
  1. "Run 50 solid validation iterations on my os-eval-runner skill"
  2. "os-eval-runner"
  3. "I have Copilot CLI and Claude available"
  4. "Success means the skill scores higher on correctness"
- **Evaluate for**: AC-1 (Category 3 within 2 turns), AC-2 (Copilot CLI not proposed until turn 3 tools answer confirmed), AC-4 (audit confirms os-eval-runner exists)
```

#### Section 4: Run Protocol

Under `## Run Protocol`, write the steps the tester follows:

```markdown
## Run Protocol

For each scenario to run:

### Step 1 — Assemble the test prompt

Write the following to `temp/test_prompt_<scenario-id>.md`:

```
SYSTEM CONTEXT (os-architect agent — read and adopt this persona):
[Read and embed the full content of plugins/agent-agentic-os/agents/os-architect-agent.md]

SIMULATION INSTRUCTION:
You are os-architect running a real intake session. Below is a transcript of a user
conversation. Process each USER turn as if the user just said it. After each USER turn,
produce your ARCHITECT response. At the end of the transcript, emit your HANDOFF_BLOCK.

Do NOT break character. Do NOT add meta-commentary. Respond only as os-architect would.

CONVERSATION TRANSCRIPT:
USER: [user_turn_1]
ARCHITECT:
USER: [user_turn_2]
ARCHITECT:
[... continue for all turns ...]
USER: [final_turn]
ARCHITECT:
[HANDOFF_BLOCK here]
```

### Step 2 — Dispatch to Copilot CLI

```bash
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null \
  temp/test_prompt_<scenario-id>.md \
  temp/test_output_<scenario-id>.md \
  "Run the os-architect intake session exactly as scripted. Adopt the os-architect persona fully." \
  claude-sonnet-4.6

wc -l temp/test_output_<scenario-id>.md  # expect 40+ lines
```

### Step 3 — Evaluate the output

Read `temp/test_output_<scenario-id>.md`. For each AC:

**AC-1**: Scan for the classification statement (intent category label). Note which turn it appears on.
- PASS if correct category stated by turn 2 of the transcript
- FAIL if wrong category or not stated within first 2 ARCHITECT responses

**AC-2**: Scan for dispatch strategy mention. Note which turn it first appears.
- PASS if dispatch strategy (copilot-cli / gemini-cli / claude-subagents) is not stated before the ARCHITECT response to user_turn_3 (tools question)
- FAIL if dispatch strategy appears in ARCHITECT response 1 or 2

**AC-3** (gap-fill scenario only): Scan for evals review gate language ("review the evals", "HARD-GATE", "approve the eval cases", or semantically equivalent).
- PASS if present before any mention of "run the loop" or "start the improvement"
- FAIL if absent or if loop is proposed before evals review

**AC-4**: Scan for audit verification language ("memory", "file-read", "verified", or a file path reference).
- PASS if present in the ARCHITECT response following turn 2
- FAIL if absent

### Step 4 — Write test report

Write to `temp/test_report_<scenario-id>.md`:

```markdown
# os-architect Test Report — <scenario-id>
Date: [today]
Model: claude-sonnet-4.6

## Scenario
[scenario description and user turns]

## Results

| Criterion | Result | Notes |
|-----------|--------|-------|
| AC-1 Intent classification | PASS / FAIL | [which turn, what was classified] |
| AC-2 Dispatch strategy gated | PASS / FAIL | [when strategy appeared] |
| AC-3 Evals HARD-GATE | PASS / FAIL / N/A | [present/absent, or N/A if not gap-fill] |
| AC-4 Audit verification cited | PASS / FAIL | [what was cited] |

## Overall: PASS / FAIL

## HANDOFF_BLOCK from transcript
[paste the HANDOFF_BLOCK emitted by os-architect in the simulation]

## Improvement Notes
[Any failure observations that suggest a fix to os-architect-agent.md]
```
```

#### Section 5: Running Multiple Scenarios

Under `## Running Multiple Scenarios`, write:

To run all 3 built-in scenarios in sequence, run each through the Run Protocol above
and then write a consolidated report to `temp/test_report_consolidated.md` summarising
total PASS/FAIL counts and any patterns across failures.

If 2 or more ACs fail across 2 or more scenarios, flag this as a regression and
recommend updating `os-architect-agent.md` before deploying.

#### Section 6: Gotchas

Write `## Gotchas` with 4 entries:

- **os-architect agent file not found**: The tester reads `plugins/agent-agentic-os/agents/os-architect-agent.md` to embed in the test prompt. If the file is missing (not yet installed to `.agents/`), the test prompt will be empty and the output will be meaningless. Always verify the agent file exists before running.
- **Single-shot simulation is approximate**: Copilot CLI runs stateless single-shot inference. The simulated multi-turn transcript is a faithful approximation but does not replicate a real interactive session exactly. Use results as signal, not ground truth.
- **AC-2 false pass**: os-architect may mention a CLI tool in a general knowledge context (e.g., "Copilot CLI is one option") without committing to a dispatch strategy. Only fail AC-2 if the strategy is explicitly stated as the selected dispatch method before the tools question.
- **Empty output from premium run**: If `test_output_<scenario-id>.md` is empty or under 10 lines, the dispatch failed silently. Re-run with `wc -l` verification before evaluating. Do not produce a test report from empty output.

---

## Workstream H — Create `plugins/agent-agentic-os/skills/os-evolution-planner/`

Create the directory, SKILL.md, and evals. This skill codifies the plan+prompt+dispatch
workflow used to build tasks 0018 and 0019. It is called by os-architect for Path B and C
executions that need a structured handoff to Copilot CLI.

### H1 — `plugins/agent-agentic-os/skills/os-evolution-planner/SKILL.md`

#### Frontmatter

```yaml
---
name: os-evolution-planner
description: >
  Codifies the plan-and-delegate workflow for evolving plugins, skills, and agents.
  Given a target (plugin/skill/agent name) and an evolution goal, this skill reviews
  the target files, identifies gaps using the self-healing diagnostic lens, writes a
  structured task plan, writes a dense Copilot CLI delegation prompt, and optionally
  dispatches it. Called by os-architect for Path B (update) and Path C (create)
  executions. Can also be invoked standalone.
model: inherit
color: blue
tools: ["Bash", "Read", "Write"]
---
```

#### Body

Write the following sections:

**Section: Role**

One paragraph: os-evolution-planner transforms an evolution goal into a structured
task plan and a Copilot CLI delegation prompt that can be dispatched in one premium request.
It applies the self-healing diagnostic lens to detect what's missing, then writes
workstream-by-workstream specifications that the delegated agent can execute without
additional context.

**Section: Inputs**

Write a table: Input | How provided | Default
- Target plugin | argument or interview question | required
- Target skill or agent | argument or interview question | "all" (full plugin audit)
- Evolution goal | argument or interview question | required
- Auto-detect gaps | flag | true
- Dispatch immediately | flag | false (present for human review)

**Section: Gap Detection Lens**

Under `## Gap Detection Lens`, write: when `auto-detect-gaps` is true, read the target
files and check for each of these. Each confirmed gap becomes one workstream:

```markdown
| Check | Gap if... | Workstream type |
|-------|-----------|-----------------|
| `## Gotchas` section | absent from SKILL.md or agent file | Add Gotchas (3–5 field-derived patterns) |
| `## HANDOFF_BLOCK` in completion | absent from child skill completion section | Add HANDOFF_BLOCK code fence |
| `evals.json` | stub (< 6 cases) or REPLACE placeholders | Fill with real routing cases |
| Model identifiers | contain dashes (claude-sonnet-4-6) | Fix to dot notation |
| Domain patterns layer | `references/domain-patterns/` absent | Create README + first pattern file |
| `## Smoke Test` | absent from SKILL.md | Add with 2–3 acceptance criteria |
| Session hook | `hooks/session_end.py` absent | Create session-end hook |
| Script security | `--dangerously-skip-permissions` unconditional | Add `--tier` flag |
```

**Section: Output Format**

Under `## Output Format`, write:

**Task plan** written to `tasks/todo/<YYYY-MM-DD>-<slug>-plan.md`:
```markdown
# <task-number> — <title>

## Context
[What triggered this evolution, what was found]

## Gaps Identified
[One bullet per gap found by the detection lens]

## Workstreams
| WS | Scope | Delegate to |
...

## Delegation Plan
1. Delegation prompt at tasks/todo/copilot_prompt_<slug>.md
2. Dispatch via run_agent.py with claude-sonnet-4.6
3. Review output (diff, symlink audit)
4. Commit and PR

## Status
- [ ] WS-A ...
```

**Delegation prompt** written to `tasks/todo/copilot_prompt_<slug>.md`:
- One section per workstream with exact file paths and content specifications
- Global instruction: "Use the Write tool to write files directly — do not output delimiters"
- Completion checklist section at the end with COMPLETION_REPORT format

**Section: Dispatch Step**

Under `## Dispatch Step`, write: if `--dispatch` flag is set (or user confirms dispatch),
run the heartbeat then dispatch:

```bash
# Heartbeat first
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat_<slug>.md \
  "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."
grep -q "HEARTBEAT_OK" temp/heartbeat_<slug>.md || (echo "HEARTBEAT FAIL — aborting dispatch" && exit 1)

# Dispatch
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null \
  tasks/todo/copilot_prompt_<slug>.md \
  temp/copilot_output_<slug>.md \
  "Generate all files exactly as specified. Use the Write tool to write files directly." \
  claude-sonnet-4.6

wc -l temp/copilot_output_<slug>.md  # expect 100+ lines for multi-workstream output
```

If dispatch flag is NOT set, present the plan and prompt paths and ask:
> "Plan written to `tasks/todo/<slug>-plan.md` and delegation prompt to
> `tasks/todo/copilot_prompt_<slug>.md`. Dispatch to Copilot CLI now? (yes / review first)"

**Section: Integration with os-architect**

Under `## Integration with os-architect`, write:

os-architect calls this skill when:
- **Path B (Update)**: a capability exists but has gaps — pass the target + list of gaps
- **Path C (Create)**: a new skill/agent is being built — pass the target name + goal description

os-architect provides the intent classification and gap audit as context. This skill writes
the plan and prompt, then either dispatches or presents for human review.

**Section: Gotchas**

Write `## Gotchas` with 4 entries:

- **Gap detection reads source files, not installed `.agents/` files**: Always read from `plugins/<plugin>/skills/<skill>/SKILL.md` — the installed `.agents/` copy may be stale. The source is authoritative.
- **Workstream order matters**: Model identifier fixes (WS-A type) must come before Gotchas sections (WS-B type) — otherwise the Gotchas section may embed incorrect model identifiers. Sort structural fixes before additive content.
- **Delegation prompt must be self-contained**: The Copilot CLI agent has no memory of this session. Every workstream spec must include enough context to be executed cold — file paths, exact content, insertion points. Never reference "as discussed" or "per the plan."
- **Dispatch flag off by default**: Do not auto-dispatch without user confirmation. The plan and prompt are the deliverable; dispatch is the next step. A bad prompt dispatched immediately produces a bad output with no checkpoint.

**Section: Smoke Test**

Write `## Smoke Test` with 2 acceptance criteria:
1. Given target = `os-eval-runner` skill with no Gotchas section, the skill writes a plan with at least 1 workstream and a delegation prompt with the Gotchas spec inline. Both files written to `tasks/todo/`.
2. Given `--dispatch` flag set and heartbeat passes, the skill calls `run_agent.py` with `claude-sonnet-4.6` and verifies output line count before reporting complete.

### H2 — `plugins/agent-agentic-os/skills/os-evolution-planner/evals/evals.json`

Create the `evals/` directory and write 9 routing cases (3 TP + 3 borderline-TP + 3 FP):

```json
[
  {"prompt": "Review the os-eval-runner skill and create a plan to improve it", "should_trigger": true},
  {"prompt": "I want to apply the browser harness self-healing patterns to exploration-cycle-plugin — write a task plan and delegation prompt", "should_trigger": true},
  {"prompt": "Create an evolution plan for the discovery-planning skill — it's missing Gotchas and HANDOFF_BLOCK", "should_trigger": true},

  {"prompt": "Help me figure out what needs to change in my agent ecosystem", "should_trigger": true},
  {"prompt": "I want to improve something in agent-agentic-os but not sure what", "should_trigger": true},
  {"prompt": "Write a delegation prompt to improve my skill", "should_trigger": true},

  {"prompt": "Run the improvement loop on os-eval-runner for 50 iterations", "should_trigger": false},
  {"prompt": "Show me the eval score for discovery-planning", "should_trigger": false},
  {"prompt": "Fix the bug in dispatch.py where the tier flag is ignored", "should_trigger": false}
]
```

---

## Workstream I — Update CLAUDE.md, GEMINI.md, and .github/copilot-instructions.md

All three files mirror each other. Add the same new section to all three.

### What to add

Find the `## Architecture` section in each file. After the architecture block (after the
closing ``` of the architecture diagram), insert this new section verbatim:

```markdown
---

## Plugin Evolution Entry Points

The agent-agentic-os plugin provides a structured workflow for evolving any plugin,
skill, or sub-agent in this repo. Three key capabilities:

| Skill / Agent | Invoke as | Purpose |
|---------------|-----------|---------|
| `os-architect` | `/os-architect` | Front-door intake — start here for any evolution activity |
| `os-evolution-planner` | called by os-architect | Writes task plans + Copilot CLI delegation prompts |
| `os-architect-tester` | agent dispatch | Validates os-architect via pre-scripted scenario transcripts |

### Evolution workflow (how tasks 0018 / 0019 were built)

1. **Invoke `/os-architect`** — describe what you want to evolve in plain language
2. **Intent classified** into one of 5 categories (pattern abstraction, research application, lab setup, gap fill, multi-loop)
3. **Ecosystem audit** — os-architect checks what exists vs what's needed
4. **Path proposed**: A (orchestrate existing) / B (update existing) / C (create new)
5. **os-evolution-planner** writes the task plan + Copilot CLI delegation prompt
6. **Dispatch** via `run_agent.py` with `claude-sonnet-4.6` (single premium request, batch everything)
7. **Validate** via `os-architect-tester` after any changes to os-architect

### Copilot CLI delegation pattern (canonical)

```bash
# 1. Heartbeat (free model — always first)
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat.md "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."

# 2. Dispatch (one dense premium request — batch all workstreams)
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null tasks/todo/copilot_prompt_<task>.md temp/copilot_output_<task>.md \
  "Generate all files exactly as specified. Use the Write tool to write files directly." \
  claude-sonnet-4.6

# 3. Verify output before claiming complete
wc -l temp/copilot_output_<task>.md  # expect 100+ lines for multi-file output
```
```

### Files to update

1. `CLAUDE.md` — insert the new section after the `## Architecture` block
2. `GEMINI.md` — insert the identical section after the `## Architecture` block
3. `.github/copilot-instructions.md` — insert the identical section after the `## Architecture` block

Read each file first to find the exact insertion point (end of the ``` architecture diagram block).
Do not modify any other content.

---

## Completion Checklist

```
## COMPLETION_REPORT
WS-G: [done / partial / skipped] — [one sentence]
WS-H-skill: [done / partial / skipped] — [one sentence]
WS-H-evals: [done / partial / skipped] — [one sentence]
WS-I: [done / partial / skipped] — [one sentence, note all 3 files updated]
FILES_CHANGED: [list of all files written or modified]
DEVIATIONS: [any spec deviations]
```
