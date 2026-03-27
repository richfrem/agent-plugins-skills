# gstack: Comparative Architecture Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Source repo:** https://github.com/garrytan/gstack
**Local copy:** `temp/gstack/`
**Output directory:** `plugin-research/gstack/`

---

## Important Context Before You Begin

gstack is architecturally the closest external reference to the richfrem plugin
ecosystem of any repo reviewed so far. Both share:

- `.agents/` as a central store for agent components
- `CLAUDE.md` conventions driving agent behavior  
- Skills as the primary knowledge primitive
- A workflow-first mindset organizing work into named operational modes

However, gstack appears to be built for a specific software team's engineering
workflow, while richfrem plugins are designed as a distributable, cross-agent
ecosystem. This distinction will shape your analysis.

Key structural signals to interpret:
- A root-level `SKILL.md` (24KB) -- unusual positioning; understand what it IS
- `SKILL.md.tmpl` -- there is a template system here
- `ETHOS.md` -- this codebase has a stated philosophy; read it first
- `conductor.json` -- an orchestration manifest; understand what it configures
- 39 subdirectories that appear to be named workflow modes (ship/, review/, guard/, canary/, etc.)
- `CHANGELOG.md` at 131KB -- extremely high signal; skim for architectural changes

---

## Step 1: Read and Internalize All Systems

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

### System C: gstack (garrytan)
```
temp/gstack/ which is a clone of https://github.com/garrytan/gstack
```

Read these files in this priority order:

**Group 1 -- Philosophy and conventions (read first):**
- `ETHOS.md` -- the stated philosophy; this shapes everything else
- `README.md`
- `CLAUDE.md` (17KB -- how agents are expected to work here)
- `AGENTS.md`
- `DESIGN.md` and `ARCHITECTURE.md`

**Group 2 -- The core skill system:**
- `SKILL.md` (24KB root-level -- understand what this actually IS and why it is at the root)
- `SKILL.md.tmpl` (the template system behind it)
- `.agents/` directory contents (what is stored here vs richfrem's `.agents/`)

**Group 3 -- Workflow mode directories (sample 5-6, not all 39):**
Read the full contents of these as representative examples:
- `ship/` -- core delivery workflow
- `review/` -- code review workflow
- `investigate/` -- debugging / research workflow
- `canary/` -- safe deployment pattern
- `guard/` -- quality gate
- `retro/` -- retrospective

For each: understand what files are inside and what the workflow actually does.

**Group 4 -- Orchestration and tooling:**
- `conductor.json`
- `autoplan/` directory
- `benchmark/` directory
- `TODOS.md` (31KB -- shows what is planned/in-progress; high signal for intent)
- `CHANGELOG.md` (131KB -- skim by section headers; look for major architectural
  decisions and evolution of the workflow system)

**Group 5 -- Browser and environment integration:**
- `BROWSER.md` (23KB -- this is a significant capability; what is it?)
- `browse/` and `connect-chrome/` directories
- `scripts/` directory overview

---

## Step 2: Produce the Analysis Report

Save all outputs to `plugin-research/gstack/`. One file per output.

---

### Output 1: `gstack-anatomy.md`

Before comparing anything, explain what gstack actually IS. Answer:

1. **What problem does gstack solve?** Who uses it and in what context?
2. **What is the root-level `SKILL.md`?** Is it one mega-skill? A meta-skill
   template? The "project SKILL.md" for the whole agent OS? Explain its role.
3. **What are the 39 workflow subdirectories?** Are they commands? Agent
   workflows? Slash commands? Skill packages? How do they get invoked?
4. **How does `conductor.json` fit in?** What does it orchestrate?
5. **What is the `.agents/` directory here?** How does it compare to richfrem's
   `.agents/` central store pattern?
6. **What is the browser integration?** What does BROWSER.md describe?
7. **How does gstack relate to Claude Code?** Is it a Claude Code plugin?
   A standalone tool? A CLAUDE.md-driven workflow system?

This output is diagnostic -- it ensures everything downstream in the analysis
is grounded in what gstack actually is, not what it looks like at a glance.

---

### Output 2: `capabilities-matrix.md`

A structured comparison table. Rows = capability dimensions. Columns = Plugin A
(agent-agentic-os) / Plugin B (exploration-cycle-plugin) / gstack.
Mark each cell: Full / Partial / Missing / Not Applicable.

Capability dimensions:
- Session memory and persistence
- Learning loops and retrospectives
- Workflow-oriented organization (named operational modes)
- Skill templating and generation
- Orchestration / conductor pattern
- Code review workflow
- Safe deployment patterns (canary, freeze, guard)
- Spec-driven or plan-driven development
- Browser and web automation integration
- Multi-agent coordination
- Hook lifecycle (session start/stop, tool validation)
- Slash command / command coverage
- Quality gates and verification steps
- Documentation and onboarding quality
- Cross-agent portability (npx skills / multi-IDE)
- Retrospective and continuous improvement support
- Exploration and discovery workflows

---

### Output 3: `strengths-and-gaps.md`

**Section 1: What gstack does exceptionally well**
Be specific. Name actual files and workflow directories. What architectural
decisions or patterns make gstack stand out?

**Section 2: What agent-agentic-os and exploration-cycle-plugin do better**
Where does the richfrem approach have genuine advantages over gstack? Consider:
portability, progressive disclosure, skill distribution, multi-IDE support,
ecosystem composability.

**Section 3: Critical weaknesses in richfrem plugins relative to gstack**
What is missing, underpowered, or not designed for that gstack handles well?
Be direct -- do not soften this.

**Section 4: Critical weaknesses in gstack**
What architectural choices in gstack would be a problem if adopted more broadly
or distributed as a cross-team, cross-IDE plugin? Where does its team-specific
design constrain its general utility?

---

### Output 4: `transferable-patterns.md`

The most actionable output. What patterns, conventions, or design decisions from
gstack should richfrem adopt?

For each transferable pattern:
- **Pattern name**
- **What gstack does** (with file reference)
- **How to adapt it for richfrem plugins** (concrete, not vague)
- **Which richfrem plugin(s) would benefit most**
- **Effort**: Small / Medium / Large

Pay special attention to:
- The workflow directory structure (is this a better command/skill organization
  than richfrem's current approach?)
- The `SKILL.md.tmpl` template system (is this better than richfrem's scaffold.py?)
- The `ETHOS.md` philosophy (what could richfrem adopt at the project-values level?)
- The `CLAUDE.md` conventions (how do they compare to richfrem's CLAUDE.md?)
- Any patterns in named workflows (ship/, guard/, canary/) that richfrem's
  exploration-cycle-plugin or spec-kitty plugin could adopt

---

### Output 5: `recommendations.md`

**Immediate actions** (port directly with no new infrastructure):
What from gstack can be adopted into richfrem skills or CLAUDE.md right now?

**New skills or plugins to build** (inspired by gstack):
What named workflows or capabilities in gstack suggest new richfrem plugin
ideas? Be specific: name the plugin, name the skill, describe what it would do.

**Philosophy and values adoption**:
Does gstack's ETHOS.md suggest any principles that richfrem's ecosystem
constitution or SKILL.md standards should incorporate?

**What NOT to copy**:
What aspects of gstack are too team-specific, too tightly coupled to their
stack, or architecturally limiting to be worth porting?

**Opinionated recommendation**:
End with a clear, specific recommendation: What is the single most valuable
thing richfrem should take from gstack and act on first? Apply your knowledge
of agentic workflow design to make this concrete, not hedged.

---

### Output 6: `architecture-diagram.mmd`

A Mermaid diagram with two panels or sections:

**Panel 1:** gstack's architecture -- how workflow modes, the conductor, the
root SKILL.md, and .agents/ connect.

**Panel 2:** richfrem's architecture -- how plugins, skills, agent-agentic-os,
and exploration-cycle-plugin connect.

**Connections between panels:** Where do they share patterns? Where could they
integrate?

Use `graph TD` or `subgraph` format. Keep node labels short.
No special characters, em dashes, or parentheses in node labels.

---

## Step 3: Self-Review

Before saving any file, verify:
1. `gstack-anatomy.md` correctly identifies what gstack actually IS -- this
   anchors everything else
2. Every claim in `strengths-and-gaps.md` references a specific file or directory
3. `transferable-patterns.md` describes patterns that richfrem can actually
   implement as skills/plugins, not things that only work inside gstack's stack
4. The Mermaid diagram is syntactically valid
5. `recommendations.md` ends with a specific, actionable recommendation

---

## Constraints

- Read `ETHOS.md` before forming any opinions -- it may reframe what you
  think you are looking at
- Do NOT assume all 39 subdirectories are the same type of component -- figure
  out what they actually are before the matrix
- Be honest about portability limits: gstack appears team-specific; that is
  not a weakness, it is a design choice with trade-offs
- Save all outputs to `plugin-research/gstack/`
- Confirm each file saved with its path and line count
