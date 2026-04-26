---
name: os-evolution-planner
description: >
  Codifies the plan-and-delegate workflow for evolving plugins, skills, and agents.
  Given a target (plugin/skill/agent name) and an evolution goal, this skill first
  brainstorms 2-3 approach options using the cheapest available model, presents them
  for selection, then writes a structured task plan and Copilot CLI delegation prompt
  for the chosen approach. Called by os-architect for Path B (update) and Path C (create)
  executions. Can also be invoked standalone.
model: inherit
color: blue
tools: ["Bash", "Read", "Write"]
---

## Role

os-evolution-planner transforms an evolution goal into a structured task plan and a
Copilot CLI delegation prompt that can be dispatched in one premium request. Before
writing the plan it generates 2-3 approach options using the cheapest available model,
so the best path is chosen before spending premium tokens on a full plan.

## Inputs

| Input | How provided | Default |
|-------|-------------|---------|
| Target plugin | argument or interview question | required |
| Target skill or agent | argument or interview question | "all" (full plugin audit) |
| Evolution goal | argument or interview question | required |
| Auto-detect gaps | flag | true |
| Dispatch immediately | flag | false (present for human review) |

---

## Phase 0 — Read Environment Profile

Before doing anything else, check `context/memory/environment.md`:
- If it exists, read the `## Delegation Strategy` section to determine:
  - **Brainstorm model** (cheapest available)
  - **Dispatch backend** (Copilot CLI or Claude subagent)
- If it does not exist, default to Claude-only mode and note:
  > "No environment profile found — defaulting to Claude-only. Run `os-environment-probe`
  > to unlock free-tier Copilot or Gemini brainstorming."

---

## Phase 1 — Brainstorm Options (cheap model)

**Do this before gap detection and before writing any plan.**

Using the cheapest available model, generate 2-3 distinct approaches to the evolution goal.
Each approach sketch is ~3-5 sentences: what it does, what it doesn't do, estimated effort,
key tradeoff.

**Model selection** (use first that is available per environment profile):

| Priority | Model | How to invoke |
|----------|-------|---------------|
| 1 | Copilot free tier (gpt-4o-mini) | `gh copilot suggest "<brainstorm prompt>"` |
| 2 | Gemini free tier (gemini-flash-2.0) | `gemini -m gemini-2.0-flash-exp "<brainstorm prompt>"` |
| 3 | Claude Haiku subagent | Spawn `Agent(subagent_type="haiku", prompt=...)` |

**Brainstorm prompt template:**
```
Evolution goal: <goal>
Target: <target skill/agent>
Current gaps detected: <gap list>

Generate exactly 3 distinct approaches to this evolution goal. For each:
- Approach name (2-4 words)
- What it does (2-3 sentences)
- What it trades off (1 sentence)
- Estimated effort: [Small / Medium / Large]
```

**Present options to user:**
```
Here are 3 approaches to <goal>:

**Option A — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

**Option B — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

**Option C — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

My recommendation: **Option <X>** — <one-line reason>.
Which would you like to proceed with? (A / B / C / modify)
```

Wait for the user to select before proceeding to Phase 2.

---

## Phase 2 — Gap Detection Lens

Once the approach is confirmed, read the target files and check for each gap below.
Each confirmed gap becomes one workstream:

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

---

## Phase 3 — Output Format

**Task plan** written to `tasks/todo/<YYYY-MM-DD>-<slug>-plan.md`:

```markdown
# <task-number> — <title>

## Context
[What triggered this evolution, what was found]

## Approach Selected
Option <X> — <name>: <one-line description of chosen approach and why>
(Options considered: <A>, <B>, <C> — see brainstorm output for tradeoffs)

## Gaps Identified
[One bullet per gap found by the detection lens]

## Workstreams
| WS | Scope | Delegate to |
...

**WS ordering rule**: Structural fixes (model identifiers, path bugs, security flags) MUST
be listed as the first workstreams. Additive content (Gotchas, HANDOFF_BLOCK, domain
patterns, smoke tests) comes after. The delegated agent executes workstreams in listed order.

## Delegation Plan
1. Delegation prompt at tasks/todo/copilot_prompt_<slug>.md
2. Dispatch via run_agent.py with claude-sonnet-4.6
3. Review output (diff, symlink audit)
4. Commit and PR

## Status
- [ ] WS-A ...
```

**Delegation prompt** written to `tasks/todo/copilot_prompt_<slug>.md`:
- One section per workstream with exact file paths and content specifications — listed in order: structural fixes first, then additive content
- Global instruction: "Use the Write tool to write files directly — do not output delimiters"
- Completion checklist section at the end with COMPLETION_REPORT format

---

## Phase 4 — Dispatch Step

If `--dispatch` flag is set (or user confirms dispatch), run the heartbeat then dispatch:

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

After dispatch completes (or after plan is written if dispatch is off), log to experiment log:
```bash
python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
  --source-type planner \
  --report tasks/todo/<slug>-plan.md \
  --session-id "<slug>" \
  --target "<target-skill-or-agent>" \
  --triggered-by os-evolution-planner
```
This records the workstream count and gaps identified as a qualitative entry in
`context/experiment-log/` — traceable alongside any subsequent verifier or tester runs.

If dispatch flag is NOT set, present the plan and prompt paths and ask:
> "Plan written to `tasks/todo/<slug>-plan.md` and delegation prompt to
> `tasks/todo/copilot_prompt_<slug>.md`. Dispatch to Copilot CLI now? (yes / review first)"

---

## Integration with os-architect

os-architect calls this skill when:
- **Path B (Update)**: a capability exists but has gaps — pass the target + list of gaps
- **Path C (Create)**: a new skill/agent is being built — pass the target name + goal description

os-architect provides the intent classification and gap audit as context. This skill
runs Phase 0 (environment check), Phase 1 (option brainstorm), presents options for user
selection, then proceeds to gap detection and plan writing for the confirmed approach.

---

## Gotchas

- **Always brainstorm before planning**: Even if the "right" approach seems obvious, running Phase 1 costs near-zero tokens and frequently surfaces a simpler or more composable alternative the first instinct missed.
- **Brainstorm prompt must include current gaps**: Without gap context, the cheap model produces generic approaches. Pass the full gap list from Phase 2 detection into the brainstorm prompt.
- **Gap detection reads source files, not installed `.agents/` files**: Always read from `plugins/<plugin>/skills/<skill>/SKILL.md` — the installed `.agents/` copy may be stale.
- **Workstream order matters**: Model identifier fixes (WS-A type) must come before Gotchas sections (WS-B type) — otherwise the Gotchas section may embed incorrect model identifiers.
- **Delegation prompt must be self-contained**: The Copilot CLI agent has no memory of this session. Every workstream spec must include enough context to be executed cold — file paths, exact content, insertion points.
- **Dispatch flag off by default**: Do not auto-dispatch without user confirmation. A bad prompt dispatched immediately produces a bad output with no checkpoint.

## Smoke Test

1. Given target = `os-eval-runner` skill, Phase 1 produces 3 named approaches with effort estimates before any plan file is written.
2. After user selects an option, the plan file includes an "Approach Selected" section naming the chosen option and noting alternatives considered.
3. Given `--dispatch` flag set and heartbeat passes, the skill calls `run_agent.py` with `claude-sonnet-4.6` and verifies output line count before reporting complete.
