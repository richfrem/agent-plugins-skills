# 0019 — os-architect: Evolution & Architecture Intake Agent

## Vision

A new interactive intake agent and skill (`os-architect`) that serves as the single
front-door to the entire Agentic OS evolution ecosystem. The user invokes `/os-architect`,
describes what they want in plain language, and the agent classifies intent, audits what
already exists, proposes the right evolution path, and dispatches work — creating new
agents or skills where gaps are found.

This solves the "where do I start" problem in agent-agentic-os. Currently a user must know
which loop to invoke, what the intake agent does vs the orchestrator, etc. The Architect
removes that burden: one entry point, full ecosystem awareness, routes everything.

---

## Plugin Placement

**`plugins/agent-agentic-os/`**

Rationale: The Architect orchestrates the OS kernel and calls exploration-cycle as a tool.
It lives where the loop infrastructure it conducts already lives. Separate plugin would
fragment the behavioral family (see feedback_plugin_grouping.md).

Artifacts:
- `skills/os-architect/SKILL.md` — skill entry point (slash command `/os-architect`)
- `skills/os-architect/evals/evals.json` — routing eval cases
- `agents/os-architect-agent.md` — the interactive conductor agent

---

## Embedded Knowledge Domains

The Architect has baked-in knowledge of the full ecosystem. No registry lookup needed —
the agent file contains a curated reference catalog. Updated when new skills are added.

### agent-agentic-os Capabilities

| Capability | Entry Point | Purpose |
|------------|-------------|---------|
| Skill improvement loop | `os-improvement-loop` | Runs eval → mutate → re-eval cycle on a skill |
| Eval lab setup | `os-eval-lab-setup` | Creates isolated sibling repo for safe iteration |
| Eval runner | `os-eval-runner` | Scores a skill against evals.json |
| Eval backport | `os-eval-backport` | Promotes lab learnings back to source skill |
| Skill improvement (targeted) | `os-skill-improvement` | Single-skill improvement, no lab |
| Optimize agent instructions | `optimize-agent-instructions` | Rewrites agent prose for clarity/performance |
| Triple-loop architect | `triple-loop-architect` agent | Sets up a full triple-loop eval lab interactively |
| Triple-loop orchestrator | `triple-loop-orchestrator` agent | Runs unattended overnight improvement iterations |
| Improvement intake | `improvement-intake-agent` | Configures a skill improvement run (narrow scope) |
| Memory manager | `os-memory-manager` | Manages persistent memory files |
| OS guide | `os-guide` | Explains the OS ecosystem |

### exploration-cycle-plugin Capabilities (used as tools)

| Capability | Entry Point | Purpose |
|------------|-------------|---------|
| Pattern abstraction / discovery | `exploration-workflow` skill | SME-facing discovery for new ideas |
| Discovery planning | `discovery-planning` skill | Structured session planning with HARD-GATE |
| Requirements capture | `business-requirements-capture` skill | Structured BRD from session brief |
| Handoff preparation | `exploration-handoff` skill | TierGate + handoff package |
| Prototype building | `prototype-builder` skill | Working prototype from requirements |
| Exploration optimizer | `exploration-optimizer` skill | Improves exploration cycle quality |

### Self-Healing Patterns (known, applied proactively)

- **Gotchas sections**: every skill/agent should have field-tested failure patterns embedded
- **HANDOFF_BLOCK**: machine-readable completion signals between agents
- **Domain patterns layer**: `references/domain-patterns/` — known failure escape strategies
- **Contribute-back reflex**: when a failure is encountered, update the source artifact

### Token Efficiency Routing

Reference table — held in reserve until Phase 1 CLI tools question is answered.
The Architect does NOT pre-populate dispatch strategy; it is determined after the
user confirms what tools they have. Never propose Copilot CLI routing to a user
who only has Claude.

| Tier | Tool | Cost | Use for |
|------|------|------|---------|
| Free | Copilot CLI (gpt-5-mini / gh copilot) | ~Free | Scaffolding, docs, simple edits, stubs |
| Cheap | Copilot CLI `--model claude-sonnet-4.6` | Low | Logic, multi-step capture, eval writing |
| Premium | Claude Code Sonnet (main session) | Moderate | Planning, prompt design, orchestration |
| High | Copilot CLI `--model claude-sonnet-4.6` (batch dense) | Premium | Complex architecture, synthesis |

**User setup detection**: Phase 1 asks which CLI tools are available (Copilot/Gemini/Claude-only)
before any dispatch strategy appears. Auto-detect via PATH check (`which gh`, `which gemini`)
and pre-fill the answer, but always confirm. Default to Claude-only if uncertain.

### Scaffolding Tool

- **`create-sub-agent`** skill in `plugins/agent-scaffolders/` — interviews user, generates
  agent `.md` with full YAML frontmatter + system prompt, validates via `validate_agent.py`
- Invoked by The Architect when Path C (Create) is selected

### Delegation Patterns (embedded — The Architect uses these to dispatch work)

The Architect is not just a router — it also knows HOW to execute. When dispatching
implementation to Copilot CLI it follows this pattern:

1. **Write delegation prompt** to `temp/copilot_prompt_<task>.md` — dense, multi-workstream spec
2. **Heartbeat check** via free model before any premium dispatch
3. **Dispatch via `run_agent.py`** — `claude-sonnet-4.6` for complex multi-file generation
4. **Yolo mode** (`copilot --yolo -p "..."`) for simpler interactive tasks
5. **Verify output** before claiming success (`wc -l`, grep for expected markers)
6. **Tier-aware dispatch** via `dispatch.py --tier` for exploration-cycle sub-agents

```bash
# Heartbeat (always first, free model)
python .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat.md "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."

# Premium dispatch (batch everything into one request)
python .agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null temp/copilot_prompt_<task>.md temp/copilot_output_<task>.md \
  "Generate all files exactly as specified. Write files directly via Write tool." \
  claude-sonnet-4.6

# Yolo mode (Copilot CLI interactive, simpler tasks)
copilot --yolo -p "$(cat temp/copilot_prompt_<task>.md)"
```

---

## Intent Classification Taxonomy

Phase 1 of the interview classifies the user's request into one of five categories:

| Category | Signal Phrases | Routes To |
|----------|----------------|-----------|
| **1. Pattern Abstraction** | "found a new way of working", "want to apply X pattern", "saw this in Y repo", "browser harness", "Karpathy", "generalize this" | exploration-cycle discovery → apply to skills/agents |
| **2. Research Application** | "found a paper", "read about X technique", "want to apply research", "new approach to Y" | exploration-cycle capture → targeted skill update |
| **3. Lab Setup / Improvement Loop** | "want to improve X skill", "run eval on Y", "optimize Z agent", "stress test", "setup a lab" | improvement-intake-agent → triple-loop-orchestrator |
| **4. Capability Gap Fill** | "need an agent that does X", "this doesn't exist yet", "want to create a new skill for Y" | create-sub-agent → eval-lab-setup → register |
| **5. Multi-Loop Orchestration** | "run multiple loops", "improve several things", "evolve the whole pipeline", "coordinate" | os-architect spawns multiple loops in parallel |

---

## Session Flow (Three Phases)

### Phase 1 — Intent Interview

Open question:
> "What would you like to evolve or build today? Describe it in your own words —
> a new pattern you found, research you want to apply, a skill you want to improve,
> a gap you've hit, or something that needs to be orchestrated."

Follow-up questions (one at a time, skip if already answered):
1. What specifically is the target? (skill name, agent name, or description of the gap)
2. What tools do you have? (Copilot / Gemini / Claude-only) — determines dispatch strategy
3. What does success look like?
4. Any time/cost constraints? (Quick check vs deep stress test)

Classify intent. State classification back to user for confirmation before proceeding.

### Phase 2 — Ecosystem Audit

**Mechanism**: This is an LLM memory lookup against the embedded knowledge catalog
in the agent file — not a live file scan. The agent reasons from its baked-in
capability table. For ambiguous cases (e.g. "does X skill already exist?"), the
agent should read the actual file at `plugins/agent-agentic-os/skills/` or
`plugins/exploration-cycle-plugin/skills/` before claiming a match or gap.
Do not hallucinate capability existence — verify by file read if uncertain.

Based on intent classification, The Architect reasons from its embedded knowledge:
- Does the needed capability already exist?
- Is an existing skill/agent close but outdated or incomplete?
- Is there a gap that requires new scaffolding?

Produces an audit summary:
```
Capability needed:    [description]
Existing match:       [skill/agent name or "none"]
Match quality:        [Full / Partial / None]
Verified by:          [memory | file-read at path/to/skill]
Recommended path:     [A / B / C]
Dispatch strategy:    [copilot-cli | gemini-cli | claude-subagents — set after Phase 1 Q2]
Estimated cost tier:  [Free / Cheap / Premium]
```

### Phase 3 — Architecture Proposal + Execution

**Path A — Orchestrate**: Capability exists. Draft run config, invoke improvement-intake-agent
or triple-loop-architect. Dispatch via selected CLI tool.

**Path B — Update**: Capability exists but is outdated or has gaps.
- Propose targeted update (which sections, what to add)
- Run os-skill-improvement or os-improvement-loop on the target
- Apply self-healing patterns if missing (gotchas, HANDOFF_BLOCK)

**Path C — Create**: Capability gap confirmed.
- Invoke `create-sub-agent` skill to scaffold the new agent
- Set up eval lab via `os-eval-lab-setup`
- Write initial evals.json for the new agent
- **HARD-GATE**: Show evals.json to the user before any loop runs.
  Poor eval quality on a freshly written set will produce meaningless iterations.
  The user must approve the eval cases explicitly before the first improvement loop.
- Register in `context/agents.json`
- Run first improvement loop as validation only after evals are approved

---

## HANDOFF_BLOCK Signal

At session close The Architect emits:

```
## HANDOFF_BLOCK
INTENT: [pattern-abstraction | research-application | lab-setup | gap-fill | multi-loop]
TARGET: [skill/agent name or "new"]
PATH: [A | B | C]
DISPATCH: [copilot-cli | gemini-cli | claude-subagents]
STATUS: [configured | running | complete | blocked]
OUTPUTS: [list of files written or agents created]
```

---

## Relationship to Existing Agents

| Agent | Relationship |
|-------|-------------|
| `improvement-intake-agent` | Sub-agent called by Path A/B for skill improvement runs. NOT replaced. |
| `triple-loop-architect` | Called by Path A/B when deep lab setup is needed. |
| `triple-loop-orchestrator` | Called for unattended overnight runs. |
| `exploration-workflow` | Called for pattern abstraction (Category 1/2). |
| `create-sub-agent` | Called for gap fill (Path C). |

---

## Pending Fix: Apply improvement-intake-agent Patch

`agents/improvement-intake-phase4c-5-patch.md` is an unapplied patch adding Phase 4c
(kernel event emission) and HANDOFF_BLOCK to the intake agent. Apply this as part of
this workstream since The Architect depends on clean handoff signals from sub-agents.

---

## Workstreams

| WS | Scope | Delegate to |
|----|-------|-------------|
| A | Write `agents/os-architect-agent.md` — full interview flow, embedded knowledge catalog, routing logic, HANDOFF_BLOCK | Copilot CLI claude-sonnet-4.6 ✅ |
| B | Write `skills/os-architect/SKILL.md` — skill entry point, description, gotchas, smoke test | Copilot CLI claude-sonnet-4.6 ✅ |
| C | Write `skills/os-architect/evals/evals.json` — 15 minimum routing cases (2 TP + 1 FP per category) | Copilot CLI claude-sonnet-4.6 ✅ |
| D | Plugin documentation updates: `evals/evals.json` (plugin-level), README entry points, improvement-intake-agent pointer | Copilot CLI claude-sonnet-4.6 ✅ |
| E | Apply `improvement-intake-phase4c-5-patch.md` into `improvement-intake-agent.md` | **Manual with diff review** — critical path |
| F | Symlink audit + install to `.agents/` via plugin_add.py | Manual — owner: richfrem |
| G | `agents/os-architect-tester-agent.md` — scenario simulator that runs os-architect via Copilot CLI with pre-scripted user turns, evaluates classification + routing output against acceptance criteria, produces test report | Copilot CLI claude-sonnet-4.6 |
| H | `skills/os-evolution-planner/SKILL.md` + evals — reusable skill that codifies the plan+prompt+dispatch workflow (as done for tasks 0018/0019): reviews a plugin/skill/agent, identifies gaps, writes task plan, writes delegation prompt, dispatches to Copilot CLI | Copilot CLI claude-sonnet-4.6 |

### WS-G Detail — os-architect-tester-agent

The tester runs a pre-scripted conversation transcript through os-architect (via Copilot CLI)
and evaluates the output. This validates that os-architect classifies correctly without
needing a live human in the loop.

**How it works:**
1. The tester selects a scenario from a built-in library (or accepts one as input)
2. Formats it as a single-shot Copilot CLI prompt: system prompt (os-architect agent file)
   + simulated conversation transcript with pre-written user turns
3. Dispatches to Copilot CLI claude-sonnet-4.6 via run_agent.py
4. Evaluates the response transcript against acceptance criteria:
   - Was intent classified correctly and within 2 turns?
   - Was dispatch strategy held until tools question answered?
   - Did Path C trigger the evals HARD-GATE?
   - Was audit verification cited before claiming match/gap?
5. Produces a structured test report with pass/fail per criterion

**Scenario library (minimum 3 built-in):**
- `pattern-abstraction`: "I found a browser harness pattern I want to apply to my agents"
- `gap-fill`: "I need an agent that monitors plugin health, it doesn't exist yet"
- `lab-setup`: "Run 50 iterations on my os-eval-runner skill"

### WS-H Detail — os-evolution-planner skill

Codifies the plan-and-delegate workflow used for tasks 0018 and 0019 as a reusable skill.
os-architect calls this when a Path B or C execution needs a structured task plan + delegation
prompt before dispatching.

**Inputs (via interview or arguments):**
- Target: plugin name, skill name, or agent name
- Evolution goal: plain-language description of what needs to change or be created
- Scope: gaps to address (or "auto-detect" to scan the target files)

**Outputs:**
- `tasks/todo/<YYYY-MM-DD>-<slug>-plan.md` — structured task plan with workstreams
- `tasks/todo/copilot_prompt_<slug>.md` — dense delegation prompt ready for dispatch
- Dispatch option: run_agent.py call to execute immediately, or present for human review

**Gap detection approach:**
- Read the target skill/agent file(s)
- Apply self-healing diagnostic lens: missing Gotchas? No HANDOFF_BLOCK? Stale evals? Wrong model identifiers? Missing domain patterns?
- For each gap found, create one workstream in the plan

---

## Delegation Plan

1. Write dense prompt at `tasks/todo/copilot_prompt_0019.md` covering WS-A through D
2. Dispatch to `claude-sonnet-4.6` via `run_agent.py`
3. Review all output (diff, symlink audit)
4. Apply improvement-intake-agent patch manually or via separate dispatch
5. Run `plugin_add.py` to install to `.agents/`
6. Smoke test — concrete acceptance criteria:
   - Given: "I found a new browser harness pattern and want to apply it to my skills"
     → agent classifies as Category 1 (Pattern Abstraction), proposes Path A or B, within 2 turns
   - Given: "I need an agent that audits plugin evals for staleness, it doesn't exist yet"
     → agent classifies as Category 4 (Gap Fill), proposes Path C, surfaces eval HARD-GATE
   - Given: "run 50 iterations on my os-eval-runner skill"
     → agent classifies as Category 3 (Lab Setup), routes to improvement-intake-agent, asks about CLI tools before proposing dispatch strategy

---

## Decisions (Closed Before Delegation)

1. **Embedded knowledge format**: Inline in the agent file for v1. External reference file
   deferred to v2 when the catalog grows large enough to warrant it. Decision: **inline**.

2. **Agent registry**: `context/agent-registry.json` deferred to v2. v1 uses embedded
   knowledge only with file-read verification for ambiguous cases. Decision: **deferred**.

3. **Multi-CLI detection**: Auto-detect via PATH check (`which gh`, `which gemini`) and
   pre-fill, but always confirm with the user before applying. Decision: **detect + confirm**.

---

## Status

- [x] A — os-architect-agent.md
- [x] B — os-architect SKILL.md
- [x] C — evals.json
- [x] D — Plugin documentation (README, plugin-level evals, intake agent pointer)
- [ ] E — Apply improvement-intake-agent patch (manual)
- [ ] F — Symlink audit + install (manual)
- [x] Delegation prompt written (copilot_prompt_0019.md)
- [ ] G — os-architect-tester-agent.md
- [ ] H — os-evolution-planner skill
- [ ] I — CLAUDE.md / GEMINI.md / copilot-instructions.md awareness update
- [x] G/H/I delegation prompt written (copilot_prompt_0019b.md)
- [ ] Smoke test passed