# Exploration Cycle Plugin

Exploration-cycle plugin for the non-linear discovery mode described in [ADR-001](../../ADRs/001_augment_spec_kitty_with_exploration_cycle.md) and the architecture docs under [architecture](README.md).

## Purpose

Provide a plugin boundary for the exploration loop that sits before, alongside, and occasionally inside the formal Spec-Kitty engineering lifecycle.

The target architecture is broader than the first implementation. The initial delivery should validate a few core capabilities in isolation before this plugin hardens into a larger workflow package.

This plugin is intended to support:

- idea, problem, and need exploration
- prototype-led discovery
- capture of business requirements, user stories, business rules, goals, issues, challenges, and opportunities
- progressive narrowing into formal specification
- targeted re-entry into discovery when engineering uncovers unresolved ambiguity

The long-term design may use a multi-agent system with:

- an outer-loop orchestrator or wrapper skill
- task-specific capture skills and agents
- prototype-building capabilities
- a handoff skill for routing outputs into specs, roadmap docs, and work packages
- an optimizer for improving the exploration workflow over repeated runs

The first working path should stay smaller:

- one combined framing-and-capture skill
- one Prototype Companion
- one Handoff Preparer
- optional prototype generation when the exploration session needs runnable software

## Optional Integration: Spec-Kitty and the Quantum Double Diamond

This plugin is **self-contained by default**. The exploration cycle runs independently and requires no other plugin.

If you are using the **spec-kitty plugin** and the **quantum double diamond framework**, an optional `planning-doc-agent` bridges the two cycles:

- **Diamond 1 → Diamond 2**: After exploration handoff, the planning-doc-agent pre-drafts `spec.md`, `plan.md`, and a tasks outline into a staging area (`exploration/planning-drafts/`). A human reviews and approves before any spec-kitty CLI commands are run.
- **Diamond 2 → Diamond 1 (re-entry)**: When the spec-kitty engineering cycle encounters unresolved ambiguity — during spec authoring, work package planning, or implementation — the planning-doc-agent scopes and triggers a new exploration cycle. Multiple re-entry cycles within a single engineering run are expected and supported.

The Spec-Kitty integration path is clearly marked `[OPTIONAL]` in all workflow, skill, and agent files. Skip it entirely if running exploration as a standalone tool.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install exploration-cycle-plugin
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/exploration-cycle-plugin
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/exploration-cycle-plugin

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install exploration-cycle-plugin
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/exploration-cycle-plugin
```

## CLI Invocation Pattern

When invoking cheap sub-agents (e.g., `requirements-doc-agent.md`) from the CLI or within workflow scripts, **do not use native bash interpolation or `stdin` piping**. 

❌ **INVALID (pipe truncation risk):**
```bash
cat session-brief.md | copilot -p "$(cat agents/requirements-doc-agent.md)" "Instruction"
```

❌ **INVALID (fragile escaping):**
```bash
prompt=$(cat agents/requirements-doc-agent.md)
prompt+=$'\n\n---\n'
prompt+=$(cat exploration/session-brief.md)
copilot -p "$prompt" "Instruction"
```

✅ **STANDARD ARCHITECTURE (dispatch wrapper):**
Always use the `dispatch.py` wrapper. It safely handles file IO, explicit `---` separations, and precise subprocess execution without context truncation.

```bash
python3 plugins/exploration-cycle-plugin/skills/exploration-workflow/scripts/dispatch.py \
  --agent plugins/exploration-cycle-plugin/agents/requirements-doc-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md \
  --instruction "Mode: business-requirements. Extract functional requirements." \
  --output exploration/captures/brd-draft.md
```

## Dependencies

### System Dependencies
- **copilot-cli**: Required for autonomous execution of sub-agents (requirements-doc-agent, etc.). Ensure it is available in your PATH.

### Python Dependencies
Standard library dependencies are assumed for the initial scaffold. If external packages are required, declare them in `requirements.in` and use the standard `pip-compile` workflow:
```bash
cd plugins/exploration-cycle-plugin
pip-compile requirements.in
pip install -r requirements.txt
```

## Plugin Components
Do NOT list plugin components in `.claude-plugin/plugin.json`; Claude auto-discovers them from the directory structure.

### Skills

- `exploration-session-brief`: near-term candidate for the combined framing-and-capture role
- `prototype-builder`: builds learning prototypes when exploration needs runnable software
- `exploration-handoff`: near-term handoff preparation capability for formal spec generation
- `exploration-orchestrator`: later-phase wrapper skill once routing policy is explicit and tested
- `business-requirements-capture`: later-phase specialization if combined capture proves overloaded
- `user-story-capture`: later-phase specialization if combined capture proves overloaded
- `exploration-optimizer`: later-phase optimizer after the core loop has a stable baseline
	- includes target-specific playbooks under `skills/exploration-optimizer/references/`, including the Spec-Kitty optimizer program

### Agents

- `exploration-cycle-orchestrator-agent.md` — Phase A active
- `intake-agent.md` — Phase A active
- `requirements-doc-agent.md` — Phase A active
- `problem-framing-agent.md` — Phase A optional interactive alternative
- `prototype-companion-agent.md` — Phase A active
- `handoff-preparer-agent.md` — Phase A active
- `planning-doc-agent.md` — Optional bridge / re-entry helper
- `requirements-scribe-agent.md` — Phase B deferred
- `exploration-loop-orchestrator.md` — Phase C deferred

### Scripts

- Plugin-level scripts can later handle session initialization, artifact routing, handoff generation, and loop-state tracking.
- Each scaffolded skill already includes its own `scripts/execute.py` placeholder.


## Design References

- [Exploration cycle architecture](../../architecture/exploration-cycle-architecture.md)
- [Exploration cycle spec](../../architecture/exploration-cycle-spec.md)
- [ADR-001](../../ADRs/001_augment_spec_kitty_with_exploration_cycle.md)

## Dependencies and Related Plugins

**agent-loops**: The orchestration patterns (learning-loop, dual-loop, orchestrator) in this plugin are sourced from the reference clone under [`temp/agent-plugins-skills/plugins/agent-loops/README.md`](README.md) rather than rebuilt here. Review that README and [`PATTERN_GUIDE.md`](../../temp/agent-plugins-skills/plugins/agent-loops/PATTERN_GUIDE.md) before designing new agent coordination in this plugin.

- Phase A is inspired by `learning-loop` for optional solo framing and by `dual-loop` for requirements capture passes
- Phase C orchestration should adapt `agent-loops/skills/orchestrator` or `agent-loops/skills/dual-loop` — do not invent a new routing layer

**autoresearch** (Karpathy): The `exploration-optimizer` skill adapts the autoresearch loop pattern (baseline-first, one-variable iteration, keep/discard, results in `evals/results.tsv`). See [`temp/autoresearch/program.md`](../../temp/autoresearch/program.md) for the source.

**doc-coauthoring**: The `requirements-doc-agent` sub-agent adapts the doc-coauthoring structured capture approach — targeted questions, brainstorm-curate-draft cycle, gap flagging with `[NEEDS HUMAN INPUT]`. The sub-agent is invoked cheaply many times via Copilot CLI rather than running in the primary agent context.

## Notes

- The current scaffold is a capability spine, not a finished implementation.
- The plugin intentionally uses capability-based skill boundaries rather than one skill per template file.
- The current build order is phased: validate core skills first, then compose them, then add orchestration, then add optimization.
- The optimizer is included as a later-phase capability, not as a requirement for the first working slice.

## Directory Structure

```text
exploration-cycle-plugin/
├── .claude-plugin/plugin.json
├── README.md
├── agents/
├── evals/
├── hooks/
├── references/
├── skills/
│   ├── business-requirements-capture/
│   ├── business-workflow-doc/
│   ├── exploration-handoff/
│   ├── exploration-optimizer/
│   ├── exploration-session-brief/
│   ├── exploration-workflow/
│   ├── user-story-capture/
│   └── deferred/
│       ├── exploration-orchestrator/
│       └── prototype-builder/
└── requirements.in
```
