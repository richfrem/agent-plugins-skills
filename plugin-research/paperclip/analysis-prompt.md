# Paperclip: Comparative Architecture Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Source repo:** https://github.com/paperclipai/paperclip
**Local copy:** `temp/paperclip/`
**Output directory:** `plugin-research/paperclip/`

---

## Important Context Before You Begin

Paperclip is the most architecturally comparable external system to richfrem's
goals of any repo reviewed in this research series. Key signals:

- Uses `.agents/` AND `.claude/` directories -- exact same central store pattern
  as richfrem
- Has `skills/paperclip-create-agent` and `skills/paperclip-create-plugin` --
  direct counterparts to richfrem's `create-sub-agent` and `create-plugin`
  scaffolders
- Has `skills/para-memory-files` -- a dedicated memory system skill (PARA method)
- Is a deployable platform (TypeScript monorepo with Docker, server, UI, CLI)
- Has a TypeScript Plugin SDK in `packages/plugins/sdk`

The core tension to analyze: richfrem builds a **distributable plugin ecosystem**
(ship skills as files via npx). Paperclip appears to be a **platform** (deployable
service + plugin marketplace). Both are solving similar problems at different layers.

Do not pre-judge. Read first, compare second.

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

### Also relevant from richfrem (for scaffolder comparison):
```
plugins/agent-scaffolders/skills/create-plugin/SKILL.md
plugins/agent-scaffolders/skills/create-skill/SKILL.md
```
Read these specifically for the scaffolder comparison in Output 3.

### System C: Paperclip (paperclipai)
```
temp/paperclip/ which is a clone of https://github.com/paperclipai/paperclip
```

Read these files in priority order:

**Group 1 -- What is this product? (read first):**
- `README.md` (13KB -- understand the product vision and target user)
- `AGENTS.md` (3.8KB -- agent working conventions)
- `releases/` directory listing and any release notes found (high signal for evolution)

**Group 2 -- The skills (highest priority for richfrem comparison):**
- `skills/paperclip/SKILL.md` (23KB -- the primary skill; what does it do?)
- `skills/paperclip/references/` -- read all files in this directory
- `skills/paperclip-create-agent/SKILL.md` -- compare directly against richfrem's `create-sub-agent`
- `skills/paperclip-create-agent/references/` -- all files
- `skills/paperclip-create-plugin/SKILL.md` -- compare directly against richfrem's `create-plugin`
- `skills/paperclip-create-plugin/references/` -- all files
- `skills/para-memory-files/SKILL.md` -- compare against richfrem's `memory-management` plugin
- `skills/para-memory-files/references/` -- all files

**Group 3 -- Platform infrastructure:**
- `packages/plugins/sdk/` -- directory listing and any index or README
- `packages/plugins/create-paperclip-plugin/` -- how they scaffold plugins programmatically
- `packages/adapters/` -- directory listing (what adapters exist?)
- `.agents/skills/` and `.claude/skills/` -- what is installed here vs the source skills/?

**Group 4 -- Product context:**
- `evals/` -- how they evaluate skills or agents
- `cli/` -- directory listing and README if present
- `doc/` or `docs/` -- any architecture or design documentation

---

## Step 2: Produce the Analysis Report

Save all outputs to `plugin-research/paperclip/`. One file per output.

---

### Output 1: `paperclip-anatomy.md`

Answer these questions before any comparison:

1. **What is paperclip as a product?** Who is the target user? What problem does
   it solve? Is it a platform, a tool, a plugin marketplace, or something else?

2. **What does the main `paperclip` skill (23KB) actually do?** Summarize its
   execution flow and key capabilities. What does it give an agent that it would
   not have otherwise?

3. **What is the PARA memory system** in `para-memory-files`?
   PARA = Projects, Areas, Resources, Archives (a PKM method by Tiago Forte).
   How has paperclip implemented it as an agent skill? What does it store,
   how does it structure memory, and what problem does it solve for long-running
   agent sessions?

4. **How does the TypeScript Plugin SDK work?** What can plugin authors build
   with it? How does this compare to richfrem's markdown-first plugin approach?

5. **What is the relationship between the `skills/` directory and `.agents/skills/`?**
   Are the skills in `skills/` the source and `.agents/skills/` the installed
   copies? Or something else?

6. **What adapters exist?** What external services or tools can paperclip connect
   to? What does this MCP-like adapter layer enable?

---

### Output 2: `scaffolder-comparison.md`

This is the most important output for richfrem's `agent-scaffolders` plugin.

Do a direct side-by-side comparison of:

| Aspect | richfrem `create-plugin` | paperclip `paperclip-create-plugin` |
|--------|--------------------------|--------------------------------------|
| Approach | Markdown skill | ? |
| Scaffolding method | scaffold.py + SKILL.md instructions | ? |
| Output format | Markdown plugin structure | ? |
| Validation | audit-plugin + ecosystem-standards | ? |
| Distribution | npx skills / plugin-installer | ? |
| Plugin SDK | Not applicable | TypeScript SDK |

And the same for the agent creators:

| Aspect | richfrem `create-sub-agent` | paperclip `paperclip-create-agent` |
|--------|-----------------------------|-------------------------------------|
| Interview process | ? | ? |
| System prompt approach | ? | ? |
| Frontmatter conventions | ? | ? |
| Tool assignment | ? | ? |
| Example block requirements | ? | ? |

For each comparison cell, cite the specific file and section you read.

Conclude this output with: **What should richfrem adopt from paperclip's
scaffolders, and what does richfrem do better?**

---

### Output 3: `memory-system-comparison.md`

Compare paperclip's `para-memory-files` skill against richfrem's memory
approach (which spans multiple skills including `memory-management`,
`session-memory-manager`, and `learning-loop`).

Questions to answer:
- What structure does PARA impose on memory? Is it well-suited for agent sessions?
- How does paperclip's skill direct the agent to read/write memory?
- Does richfrem's memory approach have equivalent structure, or is it ad-hoc?
- What are the trade-offs of PARA (structured method) vs richfrem's tiered
  approach (session context, hot cache, deep storage)?
- Should richfrem adopt PARA or elements of it? Why or why not?

---

### Output 4: `capabilities-matrix.md`

Structured comparison table. Rows = capability dimensions. Columns = Plugin A /
Plugin B / Paperclip. Mark: Full / Partial / Missing / Not Applicable.

Dimensions:
- Session memory and persistence
- Structured memory (PARA or equivalent)
- Learning loops and retrospective support
- Plugin creation scaffolding
- Agent creation scaffolding
- Plugin SDK (TypeScript / programmatic)
- Plugin distribution and marketplace
- Adapter / connector layer (external services)
- Evaluation framework for skills/agents
- Multi-agent coordination
- Hook lifecycle support
- Cross-agent portability
- Docker / deployment support
- Exploration and discovery workflows
- Spec-driven or plan-driven development

---

### Output 5: `strengths-and-gaps.md`

**Section 1: What paperclip does exceptionally well**
Be specific. Reference actual files and design decisions.

**Section 2: What richfrem's approach does better**
Where does the markdown-first, cross-agent, zero-install approach win?

**Section 3: Gaps in richfrem relative to paperclip**
What is missing or weaker? Be direct.

**Section 4: Gaps in paperclip relative to richfrem**
What does the platform approach sacrifice compared to the richfrem ecosystem
approach? Consider: portability, zero-dependency install, progressive disclosure,
multi-IDE support, community composability.

---

### Output 6: `recommendations.md`

**For richfrem's agent-scaffolders plugin:**
What should change in `create-plugin`, `create-skill`, or `create-sub-agent`
based on what paperclip's scaffolders demonstrate?

**For richfrem's memory management:**
Should richfrem adopt PARA? Add a new `para-memory` skill? Restructure how
memory-management works?

**For richfrem's plugin ecosystem overall:**
Does paperclip suggest richfrem should build a TypeScript Plugin SDK? Or is
the markdown-first approach fundamentally better for the cross-agent goal?

**New plugins or skills to consider:**
What capabilities in paperclip should exist as new richfrem plugin(s)?

**Opinionated recommendation:**
End with a single clear recommendation: What is the most valuable thing richfrem
should take from paperclip and build or change? Be specific and decisive.

---

### Output 7: `architecture-diagram.mmd`

A Mermaid diagram with:

**Left side:** Paperclip's architecture -- platform, skills, SDK, adapters, server/UI

**Right side:** richfrem's architecture -- plugin ecosystem, skills, bridge installer,
npx distribution, agent-agentic-os, exploration-cycle-plugin

**Connections/comparisons:** Show where they overlap, where they diverge, and
where richfrem could adopt a layer that paperclip has built.

Use `graph TD` or `subgraph` blocks. Short node labels, no special characters
or em dashes in labels.

---

## Step 3: Self-Review

Before saving any file:
1. `paperclip-anatomy.md` clearly explains what paperclip IS before any comparison
2. `scaffolder-comparison.md` cites specific file sections for every comparison cell
3. `memory-system-comparison.md` gives a clear recommendation on PARA adoption
4. Every recommendation is specific enough to act on without further clarification
5. The Mermaid diagram is syntactically valid
6. `recommendations.md` ends with one clear, opinionated decision

---

## Constraints

- Read the `para-memory-files` skill fully -- it is likely the most novel
  pattern relative to richfrem's current approach
- Compare the scaffolders (`create-plugin` vs `paperclip-create-plugin`) with
  genuine curiosity -- paperclip may have solved things richfrem has not, and
  vice versa
- Do NOT assume the TypeScript SDK is better than the markdown approach -- analyze
  the actual trade-offs for richfrem's specific goal (cross-agent distribution)
- Save all outputs to `plugin-research/paperclip/`
- Confirm each file saved with its path and line count
