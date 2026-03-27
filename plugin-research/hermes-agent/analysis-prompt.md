# Hermes Agent: Comparative Architecture Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Source repo:** https://github.com/nousresearch/hermes-agent
**Local copy:** `temp/hermes-agent/`
**Output directory:** `plugin-research/hermes-agent/`

---

## Important Context Before You Begin

Hermes Agent is NOT a Claude Code plugin ecosystem. It is a standalone Python
agent runtime built by Nous Research. You are comparing two fundamentally
different architectural tiers:

- **richfrem plugins** (agent-agentic-os, exploration-cycle-plugin): Skill/plugin
  ecosystems built on top of existing IDE agents (Claude Code, Antigravity, Copilot).
  They extend what those agents can do through markdown-first Skills and commands.

- **Hermes Agent**: A full Python agent runtime -- its own execution engine, state
  machine, tool composition system, model routing, context compression, and
  multi-agent coordination layer.

These are different layers of the stack. Your analysis must be honest about this
difference. Do NOT treat missing features as gaps -- instead, ask: "What
architectural patterns or philosophies in Hermes are worth borrowing?"

---

## Step 1: Read and Internalize the Systems

### Plugin A: agent-agentic-os (richfrem)
```
plugins/agent-agentic-os/
```
Priority files:
- `README.md` and `SUMMARY.md`
- All `skills/` subdirectories (each SKILL.md)
- All `agents/` files
- All `commands/` files
- `hooks/hooks.json`
- `references/` directory

### Plugin B: exploration-cycle-plugin (richfrem)
```
plugins/exploration-cycle-plugin/
```
Priority files:
- `README.md`
- All `skills/` subdirectories
- All `agents/` files
- All `commands/` files
- `references/` and `templates/` directories

### System C: Hermes Agent (Nous Research)
```
temp/hermes-agent/ which is a clone of https://github.com/nousresearch/hermes-agent
```

Read these files in this order -- stop after each group and process before
continuing (this is a large repo and you need to be selective):

**Group 1 -- Architecture and Philosophy (read first):**
- `README.md`
- `AGENTS.md` (17KB -- this is the core agent protocol and working conventions)
- `RELEASE_v0.2.0.md`, `RELEASE_v0.3.0.md`, `RELEASE_v0.4.0.md` (skim for
  architectural decisions and evolution -- these are high signal)

**Group 2 -- Core Runtime (read selectively):**
- `hermes_state.py` (50KB state machine -- read the class definitions and
  docstrings, not line-by-line)
- `agent/smart_model_routing.py` (how it routes between models)
- `agent/context_compressor.py` (context management approach)
- `agent/prompt_builder.py` (how prompts are constructed)
- `agent/skill_commands.py` (how skills integrate into the runtime)
- `toolsets.py` (tool composition -- read class definitions and organization)

**Group 3 -- Skill Organization (sample, do not read all 26 categories):**
- `skills/software-development/` -- one full category read
- `skills/research/` -- one full category read
- `skills/autonomous-ai-agents/` -- one full category read
- `optional-skills/DESCRIPTION.md`

**Group 4 -- Multi-Agent and Coordination:**
- `honcho_integration/` (if present -- multi-agent framework integration)
- `acp_adapter/` directory listing and any README (Agent Communication Protocol)
- `.plans/` and `plans/` directory overview

---

## Step 2: Produce the Analysis Report

Save all outputs to `plugin-research/hermes-agent/`. One file per output.

---

### Output 1: `architectural-tier-comparison.md`

**Frame this as a layer-cake diagram (text)** showing where Hermes and richfrem
plugins sit in the stack:

```
[ LLM Model Layer ]
[ Agent Runtime Layer ] <-- Hermes lives here
[ Plugin/Skill Layer  ] <-- richfrem plugins live here
[ IDE / CLI Layer     ]
```

Then answer for each layer:
- What does Hermes implement at this layer?
- What does richfrem implement at this layer?
- Where do they overlap? Where are they complementary?
- What does richfrem assume exists at the layer below (that Hermes builds itself)?

This framing prevents false gap analysis -- it clarifies what each system is
actually responsible for.

---

### Output 2: `hermes-capabilities.md`

A focused inventory of what Hermes does that is architecturally interesting,
regardless of whether richfrem does it too. For each capability:

- **Name and description** of the capability
- **Which file(s) implement it**
- **Why it is interesting architecturally**
- **Transferability rating**: High (could be adapted as a skill/plugin pattern) /
  Medium (informative but requires a custom runtime to implement) /
  Low (deeply tied to Hermes's Python runtime)

Capability areas to cover (add more from your reading):
- State machine design (`hermes_state.py`)
- Context compression strategy
- Smart model routing (cheap vs expensive model decisions)
- Skill loading and discovery
- Tool composition and toolset distribution
- Multi-agent coordination (Honcho integration if present)
- Agent Communication Protocol (ACP adapter)
- Session and trajectory management
- RL/training data generation (`rl_cli.py`, `batch_runner.py`)
- Prompt construction and caching

---

### Output 3: `transferable-patterns.md`

The most important output. What can richfrem's plugin ecosystem actually
borrow from Hermes, given that richfrem builds on top of existing IDE agents
rather than building its own runtime?

For each transferable pattern:
- **Pattern name**
- **What Hermes does** (with file reference)
- **Equivalent approach for richfrem skills/plugins** (concrete, not vague)
- **Effort to implement as a skill or plugin component**:
  Small / Medium / Large
- **Which richfrem plugin(s) would benefit most**

Focus especially on:
- Skill organization philosophies (how Hermes categorizes 26+ skill domains)
- Prompting patterns in `AGENTS.md` (which conventions shape how agents behave)
- Context management heuristics (when to compress, what to preserve)
- Tool composition strategies (how skills declare and compose toolsets)
- Plan-execute patterns (`.plans/` directory approach)

---

### Output 4: `critical-comparison.md`

**Section 1: Where Hermes is genuinely better**
Be specific about what architectural decisions in Hermes are superior for its
intended use case. Reference actual file names and design choices.

**Section 2: Where richfrem's plugin approach is genuinely better**
What advantages does the richfrem markdown-first, skills-as-filesystem approach
have over a full Python runtime? Consider: portability, maintenance, IDE
integration, zero-install distribution, progressive disclosure.

**Section 3: Where they solve the same problem differently**
Identify 3-5 cases where both approaches tackle the same fundamental problem
but with different trade-offs. Analyze the trade-offs honestly.

**Section 4: What richfrem is missing that matters**
Even given the architectural tier difference, what concepts from Hermes should
influence how richfrem designs its skills and plugins? Focus on transferable
philosophy, not features that require a Python runtime.

---

### Output 5: `recommendations.md`

Strategic recommendations for how the richfrem plugin ecosystem should respond
to what Hermes demonstrates is possible.

Structure as three sections:

**Immediate opportunities (adapt now -- no runtime needed)**
What conventions, organization patterns, or prompt architectures from Hermes
can be adopted directly into richfrem skills and plugins?

**Medium-term opportunities (worth building)**
What capabilities demonstrated by Hermes suggest richfrem should build new
skills or plugins? Be specific about what those would be.

**Strategic considerations**
- Should richfrem consider wrapping or integrating Hermes for certain use cases?
- Is there a Hermes skill category that richfrem is particularly missing?
- What does Hermes's trajectory (releases v0.2 through v0.4) suggest about
  where agentic AI tooling is heading?

End with a one-paragraph opinionated recommendation: What is the single most
valuable thing richfrem should take from this analysis and act on?

---

### Output 6: `architecture-diagram.mmd`

A Mermaid diagram showing:
- Hermes Agent architecture (runtime, state, tools, skills)
- richfrem plugin architecture (IDE agent, skills, hooks, commands)
- Their relationship to each other (complementary layers, not competitors)
- Any integration points where they could theoretically connect

Use `graph TD` format. Keep node labels short and readable.
Do not use special characters, em dashes, or parentheses inside node labels.

---

## Step 3: Self-Review

Before saving any file, verify:
1. Every claim is grounded in a file you actually read
2. The architectural tier analysis is honest -- do not conflate different layers
3. The `transferable-patterns.md` contains only patterns Claude Code skills can
   actually implement -- not Python runtime features dressed up as skill ideas
4. The Mermaid diagram is syntactically valid
5. `recommendations.md` ends with a clear, specific, opinionated recommendation

---

## Constraints

- Do NOT treat "Hermes has it, richfrem doesn't" as automatically a gap to fill.
  Always ask: is this gap meaningful given richfrem's different architectural tier?
- Do use your deep knowledge of both agentic AI architecture AND Claude Code
  plugin design to contextualize findings beyond what is literally in the files.
- Save all outputs to `plugin-research/hermes-agent/`.
- Confirm each file saved with its path and line count.
